import torch
import torch.nn as nn

def get_loss_fn(class_weights=None, label_smoothing=0.1, device='cpu'):
    """
    Returns the loss function with anti-overfitting measures.
    
    Args:
        class_weights: Optional list or tensor of weights for each class.
        label_smoothing: Float between 0 and 1, prevents overconfident predictions.
        device: 'cpu' or 'cuda' torch device.
    """
    weight_tensor = None
    if class_weights is not None:
        weight_tensor = torch.tensor(class_weights, dtype=torch.float32).to(device)
        
    criterion = nn.CrossEntropyLoss(weight=weight_tensor, label_smoothing=label_smoothing)
    return criterion
