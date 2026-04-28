import torch
import torch.nn.functional as F
from tqdm import tqdm
import os
from evaluation.metrics import compute_metrics
from utils.logger import CSVLogger
from utils.io_utils import save_checkpoint
from utils.early_stopping import EarlyStopping

class Trainer:
    def __init__(self, model, train_loader, val_loader, criterion, optimizer, scheduler, config, device, logger):
        self.model = model
        self.train_loader = train_loader
        self.val_loader = val_loader
        self.criterion = criterion
        self.optimizer = optimizer
        self.scheduler = scheduler
        self.config = config
        self.device = device
        self.logger = logger
        
        # Anti-overfitting measures
        self.early_stopping = EarlyStopping(patience=config.get('early_stopping_patience', 10), verbose=True)
        self.gradient_clip_norm = config.get('gradient_clip_norm', 1.0)
        self.experiment_name = config.get('experiment_name', 'default_exp')
        self.checkpoint_dir = config.get('checkpoint_dir', 'outputs/checkpoints/')
        
        # Determine active modalities
        self.active_mods = model.active_modalities if hasattr(model, 'active_modalities') else getattr(model, 'module', model).active_modalities
        self.consistency_lambda = float(config.get('consistency_lambda', 0.0))
        self.consistency_temperature = float(config.get('consistency_temperature', 2.0))

    def _unpack_batch(self, batch):
        leaf, uav, satellite, labels = batch
        
        # Prepare kwargs for the model forward pass based on active branches
        kwargs = {}
        if 'leaf' in self.active_mods: kwargs['leaf'] = leaf.to(self.device)
        if 'uav' in self.active_mods: kwargs['uav'] = uav.to(self.device)
        if 'satellite' in self.active_mods: kwargs['satellite'] = satellite.to(self.device)
            
        labels = labels.to(self.device)
        return kwargs, labels

    def train_epoch(self):
        self.model.train()
        running_loss = 0.0
        all_preds = []
        all_labels = []
        
        pbar = tqdm(self.train_loader, desc='Training')
        for batch in pbar:
            kwargs, labels = self._unpack_batch(batch)
            
            self.optimizer.zero_grad()
            outputs, aux = self.model(**kwargs, return_aux=True)
            ce_loss = self.criterion(outputs, labels)

            cons_loss = torch.tensor(0.0, device=self.device)
            if (
                self.consistency_lambda > 0.0
                and 'leaf' in self.active_mods
                and 'uav' in self.active_mods
                and 'leaf_logits' in aux
                and 'uav_logits' in aux
            ):
                t = self.consistency_temperature
                p_l = F.log_softmax(aux['leaf_logits'] / t, dim=1)
                p_u = F.softmax(aux['uav_logits'] / t, dim=1)
                cons_loss = F.kl_div(p_l, p_u, reduction='batchmean') * (t * t)

            loss = ce_loss + self.consistency_lambda * cons_loss
            
            loss.backward()
            # Anti-overfitting: Gradient Clipping
            torch.nn.utils.clip_grad_norm_(self.model.parameters(), self.gradient_clip_norm)
            self.optimizer.step()
            
            running_loss += loss.item()
            _, preds = torch.max(outputs, 1)
            
            all_preds.extend(preds.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())
            
            pbar.set_postfix({'loss': loss.item(), 'ce': ce_loss.item(), 'cons': cons_loss.item()})
            
        epoch_loss = running_loss / len(self.train_loader)
        metrics = compute_metrics(all_labels, all_preds)
        
        if self.scheduler:
            self.scheduler.step()
            
        return {'loss': epoch_loss, **metrics}

    @torch.no_grad()
    def validate_epoch(self):
        self.model.eval()
        running_loss = 0.0
        all_preds = []
        all_labels = []
        
        pbar = tqdm(self.val_loader, desc='Validation')
        for batch in pbar:
            kwargs, labels = self._unpack_batch(batch)
            
            outputs = self.model(**kwargs)
            loss = self.criterion(outputs, labels)
            running_loss += loss.item()
            
            _, preds = torch.max(outputs, 1)
            all_preds.extend(preds.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())
            
        epoch_loss = running_loss / len(self.val_loader)
        metrics = compute_metrics(all_labels, all_preds)
        
        return {'loss': epoch_loss, **metrics}

    def fit(self, epochs: int):
        self.logger.info(f"Starting training for {epochs} epochs on {self.device}...")
        
        csv_path = os.path.join(self.config.get('log_dir', 'outputs/metrics'), f"{self.experiment_name}_log.csv")
        csv_logger = CSVLogger(csv_path, fieldnames=['epoch', 'train_loss', 'val_loss', 'train_acc', 'val_acc', 'val_f1'])
        
        best_val_loss = float('inf')
        early_stop_epoch = None
        
        history = {'train_loss': [], 'val_loss': [], 'train_acc': [], 'val_acc': []}
        
        overfitting_warning_triggered = False
        
        for epoch in range(1, epochs + 1):
            self.logger.info(f"Epoch {epoch}/{epochs}")
            
            train_results = self.train_epoch()
            val_results = self.validate_epoch()
            
            # Record history
            history['train_loss'].append(train_results['loss'])
            history['val_loss'].append(val_results['loss'])
            history['train_acc'].append(train_results['accuracy'])
            history['val_acc'].append(val_results['accuracy'])
            
            self.logger.info(f"Train Loss: {train_results['loss']:.4f} | Train Acc: {train_results['accuracy']:.4f}")
            self.logger.info(f"Val Loss:   {val_results['loss']:.4f} | Val Acc:   {val_results['accuracy']:.4f} | Val F1: {val_results['f1_macro']:.4f}")
            
            # Anti-overfitting: Train/Val gap monitoring
            gap = train_results['accuracy'] - val_results['accuracy']
            if gap > 0.15:
                self.logger.warning(f"⚠️ Large train/val accuracy gap detected: {gap*100:.1f}%. Model may be overfitting.")
                if gap > 0.20:
                    overfitting_warning_triggered = True
            
            # Log to CSV
            csv_logger.log({
                'epoch': epoch,
                'train_loss': train_results['loss'],
                'val_loss': val_results['loss'],
                'train_acc': train_results['accuracy'],
                'val_acc': val_results['accuracy'],
                'val_f1': val_results['f1_macro']
            })
            
            # Save every epoch and keep a separate best checkpoint.
            is_best = val_results['loss'] < best_val_loss
            if is_best:
                best_val_loss = val_results['loss']
                
            save_state = {
                'epoch': epoch,
                'state_dict': self.model.state_dict(),
                'best_val_loss': best_val_loss,
                'optimizer': self.optimizer.state_dict(),
                'metrics': val_results
            }
            save_checkpoint(save_state, is_best, self.checkpoint_dir, self.experiment_name, epoch)
            
            # Track patience using the early stopper, but only stop once patience is exhausted.
            self.early_stopping(val_results['loss'])
            if self.early_stopping.early_stop:
                self.logger.info(f"Early stopping triggered at epoch {epoch}")
                early_stop_epoch = epoch
                break
                
        if overfitting_warning_triggered or (history['train_acc'][-1] - history['val_acc'][-1] > 0.20):
            print("\n⚠️ WARNING: Possible overfitting detected.")
            print(f"   Final Train acc: {history['train_acc'][-1]*100:.1f}% | Val acc: {history['val_acc'][-1]*100:.1f}%")
            print("   Consider: increasing dropout, reducing model capacity, or collecting more data.\n")
                
        return history, early_stop_epoch
