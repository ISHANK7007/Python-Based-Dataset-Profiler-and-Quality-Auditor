from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Set, Tuple
from datetime import datetime
from enum import Enum
import json


class DataType(Enum):
    """Enum representing inferred data types."""
    UNKNOWN = "unknown"
    NUMERIC = "numeric"
    INTEGER = "integer"
    FLOAT = "float"
    STRING = "string"
    BOOLEAN = "boolean"
    DATETIME = "datetime"
    CATEGORICAL = "categorical"
    ARRAY = "array"
    OBJECT = "object"
    NULL = "null"


@dataclass
class ColumnProfile:
    """Profile for a single column in the dataset."""
    name: str
    inferred_type: DataType = DataType.UNKNOWN
    
    # Basic statistics
    count: int = 0
    missing_count: int = 0
    unique_count: Optional[int] = None
    
    # Type-specific metrics
    min_value: Any = None
    max_value: Any = None
    mean: Optional[float] = None
    median: Optional[float] = None
    std_dev: Optional[float] = None
    
    # Distribution information
    frequent_values: Dict[Any, int] = field(default_factory=dict)
    histogram_bins: Optional[List[Tuple[Any, int]]] = None
    
    # Quality metrics
    has_duplicates: bool = False
    empty_string_count: int = 0
    
    # For categorical/string data
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    
    # Pattern detection
    detected_patterns: Optional[Dict[str, int]] = None
    
    def compute_missing_percentage(self) -> float:
        """Calculate percentage of missing values."""
        if self.count == 0:
            return 0.0
        return (self.missing_count / self.count) * 100
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert profile to dictionary format."""
        result = {
            "name": self.name,
            "inferred_type": self.inferred_type.value,
            "count": self.count,
            "missing_count": self.missing_count,
            "missing_percentage": self.compute_missing_percentage(),
        }
        
        # Add optional fields if they are not None or empty
        if self.unique_count is not None:
            result["unique_count"] = self.unique_count
            
        for attr in ["min_value", "max_value", "mean", "median", "std_dev"]:
            if getattr(self, attr) is not None:
                result[attr] = getattr(self, attr)
                
        if self.frequent_values:
            result["frequent_values"] = self.frequent_values
            
        if self.min_length is not None:
            result["min_length"] = self.min_length
            
        if self.max_length is not None:
            result["max_length"] = self.max_length
        
        return result


class DatasetProfile:
    """Profile containing metadata and statistics about a dataset."""
    
    def __init__(self, 
                dataset_path: str, 
                dataset_name: Optional[str] = None,
                file_format: Optional[str] = None):
        # Basic metadata
        self.dataset_path = dataset_path
        self.dataset_name = dataset_name or self._extract_name_from_path(dataset_path)
        self.file_format = file_format
        self.profile_timestamp = datetime.now()
        
        # Dataset metrics
        self.row_count = 0
        self.column_count = 0
        self.total_size_bytes = 0
        
        # Column-level profiles
        self.column_profiles: Dict[str, ColumnProfile] = {}
        
        # Quality metrics
        self.missing_cells_count = 0
        self.duplicate_rows_count = 0
        
        # Schema information
        self.detected_schema: Dict[str, str] = {}
        
        # Processing metadata
        self.processing_time_ms = 0
        self.profiling_errors: List[str] = []
        self.warnings: List[str] = []
    
    def _extract_name_from_path(self, path: str) -> str:
        """Extract dataset name from file path."""
        import os
        return os.path.basename(path)
    
    def add_column_profile(self, column_name: str, profile: ColumnProfile) -> None:
        """Add or update a column profile."""
        self.column_profiles[column_name] = profile
        # Update dataset-wide stats based on column
        self.missing_cells_count += profile.missing_count
    
    def compute_missing_cells_percentage(self) -> float:
        """Calculate percentage of missing values across the entire dataset."""
        total_cells = self.row_count * self.column_count
        if total_cells == 0:
            return 0.0
        return (self.missing_cells_count / total_cells) * 100
    
    def get_column_types(self) -> Dict[str, str]:
        """Get map of column names to their inferred types."""
        return {name: profile.inferred_type.value 
                for name, profile in self.column_profiles.items()}
    
    def get_completeness_score(self) -> float:
        """Calculate overall completeness score (0-100%)."""
        total_cells = self.row_count * self.column_count
        if total_cells == 0:
            return 100.0
        return 100 - self.compute_missing_cells_percentage()
    
    def get_columns_by_type(self, data_type: DataType) -> List[str]:
        """Get list of columns that match the specified type."""
        return [name for name, profile in self.column_profiles.items() 
                if profile.inferred_type == data_type]
    
    def get_problematic_columns(self, missing_threshold: float = 50.0) -> List[str]:
        """Get columns with high percentage of missing values."""
        return [name for name, profile in self.column_profiles.items() 
                if profile.compute_missing_percentage() > missing_threshold]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the entire profile to a dictionary."""
        return {
            "dataset_metadata": {
                "name": self.dataset_name,
                "path": self.dataset_path,
                "format": self.file_format,
                "profile_timestamp": self.profile_timestamp.isoformat(),
                "total_size_bytes": self.total_size_bytes
            },
            "dataset_stats": {
                "row_count": self.row_count,
                "column_count": self.column_count,
                "missing_cells_count": self.missing_cells_count,
                "missing_cells_percentage": self.compute_missing_cells_percentage(),
                "duplicate_rows_count": self.duplicate_rows_count,
                "completeness_score": self.get_completeness_score()
            },
            "column_profiles": {
                name: profile.to_dict() for name, profile in self.column_profiles.items()
            },
            "processing_info": {
                "processing_time_ms": self.processing_time_ms,
                "errors": self.profiling_errors,
                "warnings": self.warnings
            }
        }
    
    def to_json(self, indent: int = 2) -> str:
        """Convert the profile to JSON format."""
        return json.dumps(self.to_dict(), indent=indent)
    
    def get_summary(self) -> str:
        """Get a textual summary of the dataset profile."""
        summary = []
        summary.append(f"Dataset: {self.dataset_name} ({self.file_format})")
        summary.append(f"Rows: {self.row_count}, Columns: {self.column_count}")
        summary.append(f"Completeness: {self.get_completeness_score():.2f}%")
        
        if self.column_count > 0:
            summary.append("\nColumn Type Summary:")
            type_counts = {}
            for profile in self.column_profiles.values():
                type_name = profile.inferred_type.value
                type_counts[type_name] = type_counts.get(type_name, 0) + 1
                
            for type_name, count in type_counts.items():
                summary.append(f"  {type_name}: {count} columns")
            
            if self.missing_cells_count > 0:
                summary.append("\nColumns with highest missing values:")
                problematic = [(name, profile.compute_missing_percentage()) 
                              for name, profile in self.column_profiles.items()
                              if profile.missing_count > 0]
                problematic.sort(key=lambda x: x[1], reverse=True)
                
                for name, pct in problematic[:5]:  # Top 5 problematic columns
                    summary.append(f"  {name}: {pct:.2f}% missing")
        
        return "\n".join(summary)