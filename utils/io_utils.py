import os
import torch
import json

def save_checkpoint(state, is_best: bool, checkpoint_dir: str, experiment_name: str, epoch: int):
    """
    Saves the model checkpoint.
    
    Args:
        state: Dictionary containing model state_dict, optimizer state, etc.
        is_best: Whether this is the best model seen so far.
        checkpoint_dir: Directory to save the checkpoint.
        experiment_name: Name of the experiment.
        epoch: Current epoch number.
    """
    os.makedirs(checkpoint_dir, exist_ok=True)
    
    filename = os.path.join(checkpoint_dir, f"{experiment_name}_epoch_{epoch}.pth")
    torch.save(state, filename)
    
    if is_best:
        best_filename = os.path.join(checkpoint_dir, f"best_{experiment_name}.pth")
        torch.save(state, best_filename)

def load_checkpoint(checkpoint_path: str, model, optimizer=None):
    """
    Loads model and optimizer states from a checkpoint.
    
    Args:
        checkpoint_path: Path to the checkpoint file.
        model: PyTorch model instance whose state will be updated.
        optimizer: PyTorch optimizer instance whose state will be updated (optional).
        
    Returns:
        epoch (int), best_val_loss (float), best_metrics (dict)
    """
    if not os.path.exists(checkpoint_path):
        raise FileNotFoundError(f"Checkpoint not found at: {checkpoint_path}")
        
    device = next(model.parameters()).device
    checkpoint = torch.load(checkpoint_path, map_location=device, weights_only=True)
    
    model.load_state_dict(checkpoint['state_dict'])
    
    if optimizer and 'optimizer' in checkpoint:
        optimizer.load_state_dict(checkpoint['optimizer'])
        
    epoch = checkpoint.get('epoch', 0)
    best_val_loss = checkpoint.get('best_val_loss', float('inf'))
    metrics = checkpoint.get('metrics', {})
    
    return epoch, best_val_loss, metrics

def save_json(data: dict, filepath: str):
    """Saves a dictionary to a JSON file."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=4)

def load_json(filepath: str) -> dict:
    """Loads a dictionary from a JSON file."""
    if not os.path.exists(filepath):
        return {}
    with open(filepath, 'r') as f:
        return json.load(f)
