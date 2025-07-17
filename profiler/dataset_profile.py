import os
import json
from datetime import datetime
from enum import Enum

class DatasetProfile:
    """Base class representing profiling results for a dataset."""
    
    def __init__(self, dataset_path, dataset_name=None):
        self.dataset_path = dataset_path
        self.dataset_name = dataset_name or os.path.basename(dataset_path)
        self.metadata = {}
        self.column_profiles = {}
        self.row_count = 0
        self.profile_timestamp = datetime.now()
        
    def add_column_profile(self, column_name, stats):
        """Add statistics for a column to the profile."""
        self.column_profiles[column_name] = stats
        
    def get_summary(self):
        """Return a summary of the dataset profile."""
        return {
            "dataset_name": self.dataset_name,
            "row_count": self.row_count,
            "column_count": len(self.column_profiles),
            "profile_timestamp": self.profile_timestamp.isoformat(),
            "columns": list(self.column_profiles.keys())
        }

    def _serialize_stat(self, stat_obj):
        """Ensure enum and datetime values are converted to JSON-safe types."""
        if isinstance(stat_obj, dict):
            return {
                k: (v.value if isinstance(v, Enum) else v)
                for k, v in stat_obj.items()
            }
        elif hasattr(stat_obj, "__dict__"):
            return {
                k: (v.value if isinstance(v, Enum) else v)
                for k, v in vars(stat_obj).items()
            }
        else:
            return stat_obj

    def to_dict(self):
        """Convert profile to dictionary representation."""
        return {
            "dataset_name": self.dataset_name,
            "dataset_path": self.dataset_path,
            "metadata": self.metadata,
            "row_count": self.row_count,
            "profile_timestamp": self.profile_timestamp.isoformat(),
            "column_profiles": {
                col: self._serialize_stat(stats)
                for col, stats in self.column_profiles.items()
            }
        }
        
    def to_json(self):
        """Convert profile to JSON representation."""
        return json.dumps(self.to_dict(), indent=2)
