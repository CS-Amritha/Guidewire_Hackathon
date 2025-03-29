"""
Exporter for saving metrics to CSV.
"""

import os
import pandas as pd


class CSVExporter:
    """Class for exporting metrics data to CSV files."""
    
    def __init__(self, data_dir="./data"):
        """
        Initialize the CSV exporter.
        
        Args:
            data_dir (str): Directory to store CSV files
        """
        self.data_dir = data_dir
        self._ensure_data_dir_exists()
    
    def _ensure_data_dir_exists(self):
        """Ensure the data directory exists."""
        os.makedirs(self.data_dir, exist_ok=True)
    
    def save_to_csv(self, data, filename="k8s_pod_metrics.csv"):
        """
        Save metrics data to a CSV file.
        
        Args:
            data (list): List of metric dictionaries
            filename (str): Name of the CSV file
        """
        filepath = os.path.join(self.data_dir, filename)
        
        # Create a DataFrame from the data
        df = pd.DataFrame(data)
        
        # Save to CSV
        df.to_csv(filepath, index=False)
        
        return filepath