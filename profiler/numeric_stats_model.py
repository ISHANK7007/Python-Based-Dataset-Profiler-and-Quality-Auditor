import numpy as np
import pandas as pd
from typing import Dict, List, Union, Any, Optional
from dataclasses import dataclass


@dataclass
class NumericColumnStats:
    """Typed model for numeric column statistics."""
    column_name: str
    count: int
    null_count: int
    null_percent: float
    mean: float
    min: float
    max: float
    stddev: float
    median: float  # 50th percentile
    q1: float      # 25th percentile
    q3: float      # 75th percentile
    iqr: float     # Interquartile range
    p10: float     # 10th percentile
    p90: float     # 90th percentile
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'NumericColumnStats':
        """Create a NumericColumnStats instance from a dictionary."""
        return cls(**data)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "column_name": self.column_name,
            "count": self.count,
            "null_count": self.null_count,
            "null_percent": self.null_percent,
            "mean": self.mean,
            "min": self.min,
            "max": self.max,
            "stddev": self.stddev,
            "median": self.median,
            "q1": self.q1,
            "q3": self.q3,
            "iqr": self.iqr,
            "p10": self.p10,
            "p90": self.p90
        }


class NumericProfiler:
    """Profiles numeric columns to calculate common statistics."""
    
    @staticmethod
    def profile_series(series: pd.Series, 
                       use_typed_model: bool = False) -> Union[Dict[str, Any], NumericColumnStats]:
        """
        Profile a Pandas Series containing numeric data.
        
        Args:
            series: Pandas Series with numeric data to profile
            use_typed_model: If True, return a NumericColumnStats object; otherwise return dict
            
        Returns:
            Dictionary or NumericColumnStats object with numeric statistics
        """
        # Filter out non-numeric values if any
        numeric_series = pd.to_numeric(series, errors='coerce')
        
        # Basic counts
        count = len(series)
        null_count = numeric_series.isna().sum()
        null_percent = (null_count / count * 100) if count > 0 else 0
        
        # Filter out nulls for further calculations
        valid_values = numeric_series.dropna()
        
        # If no valid values after filtering, return with defaults
        if len(valid_values) == 0:
            result = {
                "column_name": series.name,
                "count": count,
                "null_count": null_count,
                "null_percent": null_percent,
                "mean": None,
                "min": None,
                "max": None,
                "stddev": None,
                "median": None,
                "q1": None,
                "q3": None,
                "iqr": None,
                "p10": None,
                "p90": None
            }
            return NumericColumnStats.from_dict(result) if use_typed_model else result
        
        # Calculate statistics
        mean_val = valid_values.mean()
        min_val = valid_values.min()
        max_val = valid_values.max()
        stddev_val = valid_values.std()
        
        # Calculate percentiles
        p10, q1, median, q3, p90 = valid_values.quantile([0.1, 0.25, 0.5, 0.75, 0.9]).values
        iqr = q3 - q1
        
        # Create result dictionary
        result = {
            "column_name": series.name,
            "count": count,
            "null_count": null_count,
            "null_percent": null_percent,
            "mean": mean_val,
            "min": min_val,
            "max": max_val,
            "stddev": stddev_val,
            "median": median,
            "q1": q1,
            "q3": q3,
            "iqr": iqr,
            "p10": p10,
            "p90": p90
        }
        
        # Return as typed model or dict based on parameter
        return NumericColumnStats.from_dict(result) if use_typed_model else result
    
    @staticmethod
    def profile_dataframe(df: pd.DataFrame, 
                         numeric_columns: Optional[List[str]] = None,
                         use_typed_model: bool = False) -> Dict[str, Union[Dict[str, Any], NumericColumnStats]]:
        """
        Profile multiple numeric columns in a DataFrame.
        
        Args:
            df: Pandas DataFrame to profile
            numeric_columns: List of column names to profile (if None, auto-detect numeric columns)
            use_typed_model: If True, return NumericColumnStats objects; otherwise return dicts
            
        Returns:
            Dictionary mapping column names to their profile statistics
        """
        # Auto-detect numeric columns if not specified
        if numeric_columns is None:
            numeric_columns = df.select_dtypes(include=['number']).columns.tolist()
        
        results = {}
        for col in numeric_columns:
            if col in df.columns:
                results[col] = NumericProfiler.profile_series(df[col], use_typed_model)
            
        return results


def profile_numeric_columns(data: Union[pd.DataFrame, pd.Series, Dict[str, List]], 
                           columns: Optional[List[str]] = None,
                           return_typed: bool = False) -> Dict[str, Union[Dict[str, Any], NumericColumnStats]]:
    """
    Convenience function to profile numeric columns from various input types.
    
    Args:
        data: Input data (DataFrame, Series, or dict of lists)
        columns: Specific columns to profile (for DataFrame or dict inputs)
        return_typed: Whether to return typed models or dictionaries
        
    Returns:
        Dictionary mapping column names to profile statistics
    """
    # Convert input to DataFrame if needed
    if isinstance(data, pd.Series):
        df = pd.DataFrame({data.name or "column": data})
        columns = [data.name or "column"]
    elif isinstance(data, dict):
        df = pd.DataFrame(data)
    else:
        df = data
    
    # Profile the data
    return NumericProfiler.profile_dataframe(df, columns, return_typed)


# Example usage
if __name__ == "__main__":
    # Sample data for demonstration
    data = {
        "numeric1": [1, 2, 3, 4, 5, None, 7, 8, 9, 10],
        "numeric2": [10.5, 20.3, 30.1, None, 50.5, 60.7, 70.9, 80.2, 90.6, 100.8],
        "text_col": ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j"]
    }
    
    # Convert to DataFrame
    df = pd.DataFrame(data)
    
    # Profile all numeric columns
    results = profile_numeric_columns(df)
    
    # Print results
    for col_name, stats in results.items():
        print(f"\nProfile for column '{col_name}':")
        for stat_name, value in stats.items():
            if stat_name != 'column_name':  # Skip the column name to avoid redundancy
                print(f"  {stat_name}: {value}")