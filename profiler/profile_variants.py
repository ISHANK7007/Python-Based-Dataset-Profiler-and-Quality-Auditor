import pandas as pd
from .dataset_profile import DatasetProfile  # Adjust import path if needed
from datetime import datetime

class CsvProfile(DatasetProfile):
    """Profile implementation for CSV datasets."""
    
    def load_data(self):
        """Loads and parses the CSV file."""
        try:
            df = pd.read_csv(self.dataset_path)
            self.row_count = len(df)
            self.metadata["columns"] = list(df.columns)
            self.metadata["file_type"] = "csv"
            self.metadata["loaded_at"] = datetime.now().isoformat()
            return df
        except Exception as e:
            self.metadata["load_error"] = str(e)
            return None


class JsonProfile(DatasetProfile):
    """Profile implementation for JSON datasets."""
    
    def load_data(self):
        """Loads and parses the JSON file."""
        try:
            df = pd.read_json(self.dataset_path, lines=True)
            self.row_count = len(df)
            self.metadata["columns"] = list(df.columns)
            self.metadata["file_type"] = "json"
            self.metadata["loaded_at"] = datetime.now().isoformat()
            return df
        except Exception as e:
            self.metadata["load_error"] = str(e)
            return None
