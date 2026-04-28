import logging
import os
import csv
from datetime import datetime

def setup_logger(log_dir: str, experiment_name: str) -> logging.Logger:
    """
    Sets up a logger that writes to both console and a log file.
    
    Args:
        log_dir: Directory where the log file will be saved.
        experiment_name: Name of the experiment to prepend to the log file.
        
    Returns:
        Configured logger instance.
    """
    os.makedirs(log_dir, exist_ok=True)
    
    logger = logging.getLogger(experiment_name)
    logger.setLevel(logging.INFO)
    
    # Avoid adding handlers multiple times if logger is already set up
    if not logger.handlers:
        # Create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        
        # File handler
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = os.path.join(log_dir, f"{experiment_name}_{timestamp}.log")
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
    return logger

class CSVLogger:
    """
    Logs epoch metrics to a CSV file.
    """
    def __init__(self, log_file: str, fieldnames: list):
        """
        Args:
            log_file: Path to the CSV file to write to.
            fieldnames: List of column names for the CSV.
        """
        self.log_file = log_file
        self.fieldnames = fieldnames
        
        # Initialize file with headers if it doesn't exist
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
        if not os.path.exists(self.log_file):
            with open(self.log_file, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=self.fieldnames)
                writer.writeheader()
                
    def log(self, metrics: dict):
        """
        Appends a row of metrics to the CSV file.
        
        Args:
            metrics: Dictionary of metric name to value mapping. Should match fieldnames.
        """
        with open(self.log_file, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=self.fieldnames)
            # Filter metrics to only include defined fieldnames
            filtered_metrics = {k: v for k, v in metrics.items() if k in self.fieldnames}
            writer.writerow(filtered_metrics)
