import matplotlib.pyplot as plt
import numpy as np
import os
import torch

def plot_training_curves(train_losses, val_losses, train_accs, val_accs, early_stop_epoch=None, save_path=None):
    """
    Plots training and validation curves.
    
    Args:
        train_losses: List of training losses.
        val_losses: List of validation losses.
        train_accs: List of training accuracies.
        val_accs: List of validation accuracies.
        early_stop_epoch: Epoch index where early stopping triggered (0-indexed).
        save_path: Path to save the plot as PNG.
    """
    epochs = range(1, len(train_losses) + 1)
    
    plt.figure(figsize=(12, 5))
    
    # Loss Plot
    plt.subplot(1, 2, 1)
    plt.plot(epochs, train_losses, 'b-', label='Train Loss')
    plt.plot(epochs, val_losses, 'r-', label='Val Loss')
    if early_stop_epoch is not None and early_stop_epoch < len(epochs):
        plt.axvline(x=early_stop_epoch + 1, color='k', linestyle='--', label='Early Stop')
    plt.title('Training and Validation Loss')
    plt.xlabel('Epochs')
    plt.ylabel('Loss')
    plt.legend()
    plt.grid(True)
    
    # Accuracy Plot
    plt.subplot(1, 2, 2)
    plt.plot(epochs, train_accs, 'b-', label='Train Acc')
    plt.plot(epochs, val_accs, 'r-', label='Val Acc')
    if early_stop_epoch is not None and early_stop_epoch < len(epochs):
        plt.axvline(x=early_stop_epoch + 1, color='k', linestyle='--', label='Early Stop')
    plt.title('Training and Validation Accuracy')
    plt.xlabel('Epochs')
    plt.ylabel('Accuracy')
    plt.legend()
    plt.grid(True)
    
    plt.tight_layout()
    
    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=300)
    
    plt.close()
    
# Optional: Implement Grad-CAM visualization here in the future
def generate_gradcam(model, image_tensor, target_class=None):
    """Placeholder for Grad-CAM generation using grad-cam package"""
    pass
