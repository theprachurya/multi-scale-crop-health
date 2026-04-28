from sklearn.metrics import accuracy_score, precision_recall_fscore_support, classification_report
import numpy as np

def compute_metrics(y_true, y_pred, class_names=['Healthy', 'Stressed', 'Diseased']) -> dict:
    """
    Computes rigorous classification metrics per the instructions.
    
    Returns:
    {
      'accuracy': float,
      'precision_macro': float,
      'recall_macro': float,
      'f1_macro': float,
      'precision_per_class': dict,
      'recall_per_class': dict,
      'f1_per_class': dict,
      'classification_report': str
    }
    """
    # y_true, y_pred can be lists or tensors
    if hasattr(y_true, 'cpu'): y_true = y_true.cpu().numpy()
    if hasattr(y_pred, 'cpu'): y_pred = y_pred.cpu().numpy()
    
    # Force 1D arrays
    y_true = np.array(y_true).flatten()
    y_pred = np.array(y_pred).flatten()
    
    acc = accuracy_score(y_true, y_pred)
    
    precision, recall, f1, _ = precision_recall_fscore_support(
        y_true, y_pred, average=None, labels=[0, 1, 2], zero_division=0)
        
    precision_macro, recall_macro, f1_macro, _ = precision_recall_fscore_support(
        y_true, y_pred, average='macro', zero_division=0)
        
    report = classification_report(y_true, y_pred, target_names=class_names, zero_division=0)
    
    return {
        'accuracy': float(acc),
        'precision_macro': float(precision_macro),
        'recall_macro': float(recall_macro),
        'f1_macro': float(f1_macro),
        'precision_per_class': {name: float(p) for name, p in zip(class_names, precision)},
        'recall_per_class': {name: float(r) for name, r in zip(class_names, recall)},
        'f1_per_class': {name: float(f) for name, f in zip(class_names, f1)},
        'classification_report': report
    }
