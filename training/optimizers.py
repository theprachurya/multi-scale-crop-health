import torch.optim as optim
from torch.optim.lr_scheduler import CosineAnnealingLR

def get_optimizer(model, config):
    """
    Returns AdamW optimizer with separated parameter groups for backbone and head.
    Anti-overfitting: Uses weight decay (L2 regularization).
    """
    backbone_lr = config.get('backbone_lr', 1e-4)
    head_lr = config.get('head_lr', 1e-3)
    weight_decay = config.get('weight_decay', 1e-4)
    
    backbone_params = []
    head_params = []
    
    for name, param in model.named_parameters():
        if not param.requires_grad:
            continue
        if 'head' in name or 'fusion' in name:
            head_params.append(param)
        else:
            backbone_params.append(param)
            
    optimizer = optim.AdamW([
        {'params': backbone_params, 'lr': backbone_lr},
        {'params': head_params, 'lr': head_lr}
    ], weight_decay=weight_decay)
    
    return optimizer

def get_scheduler(optimizer, config):
    """
    Returns CosineAnnealingLR learning rate scheduler.
    """
    epochs = config.get('epochs', 60)
    scheduler = CosineAnnealingLR(optimizer, T_max=epochs, eta_min=1e-6)
    return scheduler
