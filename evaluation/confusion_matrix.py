import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix
import numpy as np
import os

def plot_confusion_matrix(y_true, y_pred, experiment_name: str, 
                          class_names=['Healthy', 'Stressed', 'Diseased'], 
                          output_dir='outputs/confusion_matrices/'):
    """
    Plots and saves a normalized confusion matrix.
    Includes both raw counts and percentages in each cell.
    """
    if hasattr(y_true, 'cpu'): y_true = y_true.cpu().numpy()
    if hasattr(y_pred, 'cpu'): y_pred = y_pred.cpu().numpy()
    
    y_true = np.array(y_true).flatten()
    y_pred = np.array(y_pred).flatten()
    
    # Compute confusion matrix
    cm = confusion_matrix(y_true, y_pred, labels=[0, 1, 2])
    
    # Calculate row-wise percentages
    cm_sum = np.sum(cm, axis=1, keepdims=True)
    # Avoid div by zero
    cm_sum[cm_sum == 0] = 1
    cm_perc = cm / cm_sum * 100
    
    # Prepare text annotations
    annot = np.empty_like(cm).astype(str)
    nrows, ncols = cm.shape
    for i in range(nrows):
        for j in range(ncols):
            c = cm[i, j]
            p = cm_perc[i, j]
            if i == j:
                annot[i, j] = f"{c}\n({p:.1f}%)"
            elif c == 0:
                annot[i, j] = "0\n(0.0%)"
            else:
                annot[i, j] = f"{c}\n({p:.1f}%)"
                
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=annot, fmt='', cmap='Blues', 
                xticklabels=class_names, yticklabels=class_names,
                cbar=False, annot_kws={"size": 12})
                
    plt.title(f'Confusion Matrix: {experiment_name}')
    plt.ylabel('True Label', fontsize=12)
    plt.xlabel('Predicted Label', fontsize=12)
    plt.tight_layout()
    
    os.makedirs(output_dir, exist_ok=True)
    save_path = os.path.join(output_dir, f'{experiment_name}_cm.png')
    plt.savefig(save_path, dpi=300)
    plt.close()
    
    return save_path
