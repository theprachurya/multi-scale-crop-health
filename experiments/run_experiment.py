import argparse
import sys
import yaml
import torch
import torch.nn as nn
import numpy as np
import random
import os

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from torch.utils.data import DataLoader
from evaluation.ablation_runner import AblationRunner
from models.multiscale_net import MultiScaleCropNet
from data.dataset import CropTripletDataset, SingleModalityDataset
from preprocessing.transforms import train_transform, val_transform
from training.loss_functions import get_loss_fn
from training.optimizers import get_optimizer, get_scheduler
from training.trainer import Trainer
from utils.logger import setup_logger
from utils.visualizer import plot_training_curves
from utils.io_utils import save_json, load_checkpoint
from evaluation.confusion_matrix import plot_confusion_matrix
from evaluation.metrics import compute_metrics
from evaluation.modality_analysis import compute_modality_contributions, summarize_fusion_weights

def set_seed(seed: int = 42):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False

def load_config(config_path: str, default_path: str = 'configs/default_config.yaml') -> dict:
    with open(default_path, 'r') as f:
        config = yaml.safe_load(f)
    if config_path and os.path.exists(config_path):
        with open(config_path, 'r') as f:
            exp_config = yaml.safe_load(f)
            config.update(exp_config)
    return config


def resolve_experiment_name(base_name: str, seed_override: int | None) -> str:
    if seed_override is None:
        return base_name
    return f"{base_name}_seed{seed_override}"

def get_dataloader(config, split='train'):
    csv_key = f"{split}_csv"
    csv_path = config.get(csv_key)
    
    if not os.path.exists(csv_path):
        print(f"Warning: {csv_path} not found. Creating a dummy loader for debugging.")
        # Ensure it does not crash during evaluation without files
        class DummySet(torch.utils.data.Dataset):
            def __len__(self): return 10
            def __getitem__(self, i): return torch.randn(3,256,256), torch.randn(3,256,256), torch.randn(3,256,256), 0
        dataset = DummySet()
    else:
        active = config.get('active_modalities', ['leaf', 'uav', 'satellite'])
        transform = train_transform if split == 'train' else val_transform
        
        if len(active) == 1:
            dataset = SingleModalityDataset(csv_path, active[0], transform=transform)
            # Need a wrapper to return 3 items to match trainer `_unpack_batch` unpack signature
            class WrapperSet(torch.utils.data.Dataset):
                def __init__(self, ds, mod):
                    self.ds = ds; self.mod = mod
                def __len__(self): return len(self.ds)
                def __getitem__(self, idx):
                    img, label = self.ds[idx]
                    leaf = img if self.mod == 'leaf' else torch.zeros_like(img)
                    uav = img if self.mod == 'uav' else torch.zeros_like(img)
                    sat = img if self.mod == 'satellite' else torch.zeros_like(img)
                    return leaf, uav, sat, label
            dataset = WrapperSet(dataset, active[0])
        else:
            # Keep tensor shapes consistent for all modalities so DataLoader collation never
            # fails in 2-modality experiments where the inactive branch still appears in batch tuples.
            l_t = transform
            u_t = transform
            s_t = transform
            dataset = CropTripletDataset(csv_path, leaf_transform=l_t, uav_transform=u_t, sat_transform=s_t)
            
    is_train = split == 'train'
    return DataLoader(dataset, batch_size=config.get('batch_size', 32), 
                      shuffle=is_train, num_workers=config.get('num_workers', 4), pin_memory=True)


def run_single_experiment(config: dict, config_path: str, seed_override: int | None):
    seed = seed_override if seed_override is not None else config.get('seed', 42)
    config['seed'] = seed
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    base_exp_name = config.get('experiment_name', 'experiment')
    exp_name = resolve_experiment_name(base_exp_name, seed_override)
    config['base_experiment_name'] = base_exp_name
    config['experiment_name'] = exp_name
    set_seed(seed)

    logger = setup_logger(config.get('log_dir', 'outputs/metrics/'), exp_name)
    logger.info(f"Loaded config from {config_path}")
    logger.info(f"Seed: {seed}")
    logger.info(f"Active modalities: {config.get('active_modalities')}")

    train_loader = get_dataloader(config, 'train')
    val_loader = get_dataloader(config, 'val')
    test_loader = get_dataloader(config, 'test')

    model = MultiScaleCropNet(
        active_modalities=config.get('active_modalities', ['leaf', 'uav', 'satellite']),
        freeze_backbones=config.get('freeze_backbones', True),
        dropout_rate=config.get('dropout_rate', 0.5),
        fusion_method=config.get('fusion_method', 'concat'),
        fusion_output_dim=config.get('fusion_output_dim', 512),
        fusion_hidden_dim=config.get('fusion_hidden_dim', 256),
    )
    model.to(device)

    criterion = get_loss_fn(label_smoothing=config.get('label_smoothing', 0.1), device=device)
    optimizer = get_optimizer(model, config)
    scheduler = get_scheduler(optimizer, config)

    trainer = Trainer(model, train_loader, val_loader, criterion, optimizer, scheduler, config, device, logger)
    history, early_stop_epoch = trainer.fit(epochs=config.get('epochs', 60))

    plot_path = os.path.join(config.get('log_dir', 'outputs/metrics/'), f"{exp_name}_curves.png")
    plot_training_curves(history['train_loss'], history['val_loss'], history['train_acc'], history['val_acc'], early_stop_epoch, plot_path)

    checkpoint_path = os.path.join(config.get('checkpoint_dir', 'outputs/checkpoints/'), f"best_{exp_name}.pth")
    if os.path.exists(checkpoint_path):
        load_checkpoint(checkpoint_path, model)
        logger.info("Loaded best checkpoint for testing.")

    model.eval()
    all_preds, all_labels = [], []
    with torch.no_grad():
        for batch in test_loader:
            kwargs, labels = trainer._unpack_batch(batch)
            outputs = model(**kwargs)
            _, preds = torch.max(outputs, 1)
            all_preds.extend(preds.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())

    test_metrics = compute_metrics(all_labels, all_preds)
    test_metrics['seed'] = int(seed)
    test_metrics['experiment_name'] = exp_name

    active_modalities = config.get('active_modalities', ['leaf', 'uav', 'satellite'])
    if len(active_modalities) > 1:
        modality_contrib = compute_modality_contributions(model, test_loader, active_modalities, device)
        test_metrics['modality_contribution'] = modality_contrib

    fusion_weights = summarize_fusion_weights(model, test_loader, active_modalities, device)
    if fusion_weights:
        test_metrics['fusion_weights'] = fusion_weights

    logger.info("\n=== Test Results ===")
    logger.info(f"Accuracy: {test_metrics['accuracy']:.4f}")
    logger.info(f"F1 Macro: {test_metrics['f1_macro']:.4f}")
    if 'fusion_weights' in test_metrics:
        logger.info(f"Fusion Weights: {test_metrics['fusion_weights']}")
    logger.info(f"\n{test_metrics['classification_report']}")

    metrics_path = os.path.join(config.get('log_dir', 'outputs/metrics/'), f"{exp_name}_metrics.json")
    save_json(test_metrics, metrics_path)

    plot_confusion_matrix(all_labels, all_preds, exp_name, output_dir=config.get('log_dir', 'outputs/metrics/').replace('metrics', 'confusion_matrices'))
    return test_metrics


def aggregate_seed_metrics(metrics_list: list[dict], seeds: list[int], base_experiment_name: str) -> dict:
    keys = ['accuracy', 'precision_macro', 'recall_macro', 'f1_macro']
    summary = {
        'experiment_name': f"{base_experiment_name}_seed_avg",
        'seeds': [int(s) for s in seeds],
        'num_seeds': len(seeds),
    }
    for k in keys:
        vals = np.array([float(m[k]) for m in metrics_list], dtype=np.float64)
        summary[f'{k}_mean'] = float(np.mean(vals))
        summary[f'{k}_std'] = float(np.std(vals, ddof=0))
    return summary

def main():
    parser = argparse.ArgumentParser(description="Multi-Scale Crop Health Training")
    parser.add_argument('--config', type=str, help='Path to experiment config YAML')
    parser.add_argument('--ablation', action='store_true', help='Run all ablation experiments')
    parser.add_argument('--seed', type=int, help='Override the experiment seed and isolate outputs for this run')
    parser.add_argument('--seeds', type=str, help='Comma-separated seeds for multi-seed averaging, e.g. 42,123,999')
    args = parser.parse_args()

    if args.ablation:
        runner = AblationRunner()
        runner.run_all()
        return

    if not args.config:
        print("Please provide a --config path or use --ablation.")
        return

    config = load_config(args.config)
    if args.seeds:
        seeds = [int(s.strip()) for s in args.seeds.split(',') if s.strip()]
        if len(seeds) == 0:
            print("No valid seeds provided in --seeds.")
            return

        all_metrics = []
        base_exp_name = config.get('experiment_name', 'experiment')
        for seed in seeds:
            seed_config = dict(config)
            metrics = run_single_experiment(seed_config, args.config, seed)
            all_metrics.append(metrics)

        summary = aggregate_seed_metrics(all_metrics, seeds, base_exp_name)
        summary_path = os.path.join(config.get('log_dir', 'outputs/metrics/'), f"{base_exp_name}_seed_summary.json")
        save_json(summary, summary_path)
        print(f"Saved multi-seed summary to {summary_path}")
        print(summary)
    else:
        run_single_experiment(config, args.config, args.seed)

if __name__ == '__main__':
    main()
