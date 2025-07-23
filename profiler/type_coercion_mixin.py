import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Union, Tuple
import logging
import os
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(),  # Log to console
        logging.FileHandler('profiler.log')  # Log to file
    ]
)
logger = logging.getLogger("dataset_profiler")


class RobustTypeCoercionMixin:
    """
    Mixin providing robust type coercion methods for handling mixed type data.
    Includes validation, coercion attempts, and error handling.
    """
    
    @staticmethod
    def try_numeric_coercion(series: pd.Series) -> Tuple[pd.Series, Dict[int, Any]]:
        """
        Attempt to coerce a series to numeric, capturing invalid values.
        
        Args:
            series: Input pandas Series
            
        Returns:
            Tuple containing: 
            - Coerced series with invalid values as NaN
            - Dictionary mapping row indices to their original invalid values
        """
        # Store original data for reference
        original_values = series.copy()
        
        # Try to convert to numeric, setting errors as NaN
        numeric_series = pd.to_numeric(series, errors='coerce')
        
        # Identify which values couldn't be converted
        invalid_mask = numeric_series.isna() & ~original_values.isna()
        invalid_indices = {}
        
        if invalid_mask.any():
            # Record the problematic indices and values
            for idx in invalid_mask[invalid_mask].index:
                invalid_indices[int(idx)] = original_values.loc[idx]
        
        return numeric_series, invalid_indices
    
    @staticmethod
    def try_datetime_coercion(series: pd.Series) -> Tuple[pd.Series, Dict[int, Any]]:
        """
        Attempt to coerce a series to datetime, capturing invalid values.
        
        Args:
            series: Input pandas Series
            
        Returns:
            Tuple containing: 
            - Coerced series with invalid values as NaN
            - Dictionary mapping row indices to their original invalid values
        """
        # Store original data
        original_values = series.copy()
        
        # Try to convert to datetime, setting errors as NaN
        try:
            datetime_series = pd.to_datetime(series, errors='coerce')
            
            # Identify which values couldn't be converted
            invalid_mask = datetime_series.isna() & ~original_values.isna()
            invalid_indices = {}
            
            if invalid_mask.any():
                # Record the problematic indices and values
                for idx in invalid_mask[invalid_mask].index:
                    invalid_indices[int(idx)] = original_values.loc[idx]
                    
            return datetime_series, invalid_indices
        
        except Exception as e:
            # Handle potential pandas errors during conversion
            logger.warning(f"Datetime coercion failed with error: {str(e)}")
            return pd.Series([pd.NaT] * len(series), index=series.index), {}
    
    @staticmethod
    def try_boolean_coercion(series: pd.Series) -> Tuple[pd.Series, Dict[int, Any]]:
        """
        Attempt to coerce a series to boolean, capturing invalid values.
        
        Args:
            series: Input pandas Series
            
        Returns:
            Tuple containing: 
            - Coerced series with invalid values as NaN
            - Dictionary mapping row indices to their original invalid values
        """
        # Store original data
        original_values = series.copy()
        
        # Define valid boolean values
        true_values = ['true', 'yes', 'y', 't', '1', 1, True]
        false_values = ['false', 'no', 'n', 'f', '0', 0, False]
        
        # Create a new series for results
        result = pd.Series(index=series.index, dtype='object')
        invalid_indices = {}
        
        # Process each value
        for idx, val in series.items():
            if pd.isna(val):
                result.loc[idx] = np.nan
            elif isinstance(val, str) and val.lower() in [str(x).lower() for x in true_values]:
                result.loc[idx] = True
            elif isinstance(val, str) and val.lower() in [str(x).lower() for x in false_values]:
                result.loc[idx] = False
            elif val in true_values:
                result.loc[idx] = True
            elif val in false_values:
                result.loc[idx] = False
            else:
                result.loc[idx] = np.nan
                invalid_indices[int(idx)] = original_values.loc[idx]
        
        return result, invalid_indices
    
    @staticmethod
    def analyze_type_consistency(series: pd.Series) -> Dict[str, Any]:
        """
        Analyze a series for type consistency and attempt to detect the most likely type.
        
        Args:
            series: Input pandas Series
            
        Returns:
            Dictionary with type analysis results
        """
        # Drop NA values for type analysis
        valid_values = series.dropna()
        
        if len(valid_values) == 0:
            return {
                "likely_type": "unknown",
                "type_consistency": 100.0,
                "type_counts": {}
            }
        
        # Count Python types in the series
        type_counts = valid_values.apply(type).value_counts().to_dict()
        
        # Calculate percentage of the most common type
        most_common_type = max(type_counts.items(), key=lambda x: x[1])
        type_consistency = most_common_type[1] / len(valid_values) * 100
        
        # Type detection heuristics
        # Try numeric coercion and check success rate
        numeric_series, numeric_errors = RobustTypeCoercionMixin.try_numeric_coercion(valid_values)
        numeric_success_rate = (len(valid_values) - len(numeric_errors)) / len(valid_values) * 100
        
        # Try datetime coercion and check success rate
        datetime_series, datetime_errors = RobustTypeCoercionMixin.try_datetime_coercion(valid_values)
        datetime_success_rate = (len(valid_values) - len(datetime_errors)) / len(valid_values) * 100
        
        # Try boolean coercion and check success rate
        boolean_series, boolean_errors = RobustTypeCoercionMixin.try_boolean_coercion(valid_values)
        boolean_success_rate = (len(valid_values) - len(boolean_errors)) / len(valid_values) * 100
        
        # Determine most likely type based on coercion success
        coercion_rates = {
            "numeric": numeric_success_rate,
            "datetime": datetime_success_rate,
            "boolean": boolean_success_rate,
            "string": 100.0  # Everything can be a string
        }
        
        likely_type = max(coercion_rates.items(), key=lambda x: x[1])[0]
        
        # Special case: if all successful types have 100% success, prefer types in this order:
        perfect_types = [k for k, v in coercion_rates.items() if v == 100.0]
        if len(perfect_types) > 1:
            type_preference = ["boolean", "numeric", "datetime", "string"]
            for preferred_type in type_preference:
                if preferred_type in perfect_types:
                    likely_type = preferred_type
                    break
        
        return {
            "likely_type": likely_type,
            "type_consistency": type_consistency,
            "type_counts": {str(k): v for k, v in type_counts.items()},  # Convert types to strings for JSON
            "coercion_rates": coercion_rates
        }


class RobustNumericProfiler(RobustTypeCoercionMixin):
    """Robustly profiles numeric columns, handling mixed data types."""
    
    @staticmethod
    def profile_series(series: pd.Series, 
                      column_name: Optional[str] = None,
                      use_typed_model: bool = False) -> Dict[str, Any]:
        """
        Robustly profile a numeric series, handling mixed types and errors.
        
        Args:
            series: The pandas Series to profile
            column_name: Name of the column (used in logging)
            use_typed_model: Whether to return a typed model (not implemented)
            
        Returns:
            Dictionary containing numeric profile statistics
        """
        actual_name = column_name or series.name or "unnamed_column"
        
        # Analyze type consistency
        type_analysis = RobustNumericProfiler.analyze_type_consistency(series)
        
        # Start with basic counts before any type coercion
        total_count = len(series)
        original_null_count = series.isna().sum()
        
        # Attempt numeric coercion, capturing invalid values
        numeric_series, invalid_values = RobustNumericProfiler.try_numeric_coercion(series)
        
        # Count nulls after coercion
        post_coercion_null_count = numeric_series.isna().sum()
        invalid_count = post_coercion_null_count - original_null_count
        
        # Log about invalid values if any were found
        if invalid_count > 0:
            logger.warning(
                f"Column '{actual_name}': {invalid_count} values couldn't be coerced to numeric. "
                f"Sample invalid values: {list(invalid_values.values())[:5]}"
            )
        
        # Valid numeric data after coercion
        valid_numeric = numeric_series.dropna()
        valid_count = len(valid_numeric)
        
        # Initialize result dictionary with counts
        result = {
            "column_name": actual_name,
            "count": total_count,
            "null_count": original_null_count,
            "invalid_count": invalid_count,
            "valid_count": valid_count,
            "null_percent": (original_null_count / total_count * 100) if total_count > 0 else 0,
            "invalid_percent": (invalid_count / total_count * 100) if total_count > 0 else 0,
            "type_consistency": type_analysis["type_consistency"],
            "likely_type": type_analysis["likely_type"],
            "sample_invalid_values": list(invalid_values.values())[:5] if invalid_values else [],
            "invalid_indices": list(invalid_values.keys())[:10] if invalid_values else []  # First 10 invalid indices
        }
        
        # If we have valid numeric data, calculate statistics
        if valid_count > 0:
            try:
                # Basic statistics
                result.update({
                    "mean": float(valid_numeric.mean()),
                    "min": float(valid_numeric.min()),
                    "max": float(valid_numeric.max()),
                    "sum": float(valid_numeric.sum()),
                    "std": float(valid_numeric.std()) if len(valid_numeric) > 1 else None,
                })
                
                # Calculate percentiles if we have enough data
                if len(valid_numeric) >= 5:  # Arbitrary threshold for meaningful percentiles
                    percentiles = [0.1, 0.25, 0.5, 0.75, 0.9]
                    percentile_values = np.percentile(valid_numeric, [p * 100 for p in percentiles])
                    
                    result.update({
                        "p10": float(percentile_values[0]),
                        "q1": float(percentile_values[1]),
                        "median": float(percentile_values[2]),
                        "q3": float(percentile_values[3]),
                        "p90": float(percentile_values[4]),
                        "iqr": float(percentile_values[3] - percentile_values[1])
                    })
                
                # Check for zeros, negative values
                result.update({
                    "zero_count": int((valid_numeric == 0).sum()),
                    "negative_count": int((valid_numeric < 0).sum()),
                    "positive_count": int((valid_numeric > 0).sum()),
                })
                
            except Exception as e:
                # Catch any other errors during statistical calculation
                logger.error(f"Error calculating statistics for column '{actual_name}': {str(e)}")
                result["calculation_error"] = str(e)
        
        return result
    
    @staticmethod
    def profile_dataframe(df: pd.DataFrame,
                         numeric_columns: Optional[List[str]] = None,
                         infer_numeric: bool = True,
                         min_type_consistency: float = 70.0) -> Dict[str, Dict[str, Any]]:
        """
        Profile multiple numeric columns in a dataframe, handling mixed types.
        
        Args:
            df: Pandas DataFrame to profile
            numeric_columns: List of columns to consider as numeric (if None, detect automatically)
            infer_numeric: Whether to try type inference for unlisted columns
            min_type_consistency: Minimum numeric type consistency threshold (%)
            
        Returns:
            Dictionary mapping column names to their numeric profiles
        """
        results = {}
        
        # If no specific columns provided, detect numeric columns
        if numeric_columns is None:
            # Start with columns pandas classifies as numeric
            numeric_columns = df.select_dtypes(include=["number"]).columns.tolist()
            
            # If inference enabled, analyze all other columns for potential numeric data
            if infer_numeric:
                non_numeric_columns = [col for col in df.columns if col not in numeric_columns]
                
                for col in non_numeric_columns:
                    try:
                        type_analysis = RobustNumericProfiler.analyze_type_consistency(df[col])
                        
                        # If column looks like it contains mostly numeric data
                        if (type_analysis["likely_type"] == "numeric" and 
                            type_analysis["coercion_rates"]["numeric"] >= min_type_consistency):
                            numeric_columns.append(col)
                            logger.info(
                                f"Column '{col}' inferred as numeric with "
                                f"{type_analysis['coercion_rates']['numeric']:.1f}% consistency"
                            )
                    except Exception as e:
                        logger.warning(f"Error analyzing column '{col}': {str(e)}")
        
        # Profile each numeric column
        for col in numeric_columns:
            if col in df.columns:
                try:
                    results[col] = RobustNumericProfiler.profile_series(df[col], col)
                except Exception as e:
                    logger.error(f"Failed to profile column '{col}': {str(e)}")
                    results[col] = {
                        "column_name": col,
                        "error": str(e),
                        "profiling_success": False
                    }
            else:
                logger.warning(f"Column '{col}' specified but not found in dataframe")
        
        return results


# Example of integrated profiler with all types
class RobustDatasetProfiler:
    """
    Main profiler class that coordinates profiling of all column types
    and integrates results into a unified dataset profile.
    """
    
    def __init__(self, log_level=logging.INFO):
        """
        Initialize the profiler with specified log level.
        
        Args:
            log_level: Logging level (default: INFO)
        """
        self.logger = logger
        self.logger.setLevel(log_level)
        
        # Track profiling operations
        self.operation_log = []
    
    def log_operation(self, operation, details=None):
        """Record an operation in the operation log."""
        timestamp = datetime.now().isoformat()
        log_entry = {"timestamp": timestamp, "operation": operation}
        
        if details:
            log_entry["details"] = details
            
        self.operation_log.append(log_entry)
    
    def profile_csv(self, csv_path: str, **kwargs) -> Dict[str, Any]:
        """
        Profile a CSV file with robust error handling.
        
        Args:
            csv_path: Path to the CSV file
            kwargs: Additional arguments for pandas.read_csv()
            
        Returns:
            Dictionary containing the complete dataset profile
        """
        self.log_operation("profile_csv", {"path": csv_path})
        
        if not os.path.exists(csv_path):
            self.logger.error(f"CSV file not found: {csv_path}")
            return {"error": f"File not found: {csv_path}"}
        
        try:
            # Attempt to read CSV with pandas, capturing any parsing errors
            try:
                # First try standard read_csv with some common options
                df = pd.read_csv(
                    csv_path, 
                    low_memory=False,  # Avoid mixed type inference issues
                    **kwargs
                )
            except Exception as e:
                self.logger.warning(f"Initial CSV parse failed, trying with error handling: {str(e)}")
                # If that fails, try with more error handling options
                df = pd.read_csv(
                    csv_path,
                    low_memory=False,
                    on_bad_lines='skip',  # Skip problematic lines
                    warn_bad_lines=True,
                    encoding='utf-8',     # Explicit encoding
                    **kwargs
                )
                self.logger.info("Successfully loaded CSV with error handling options")
            
            # Basic dataset info
            file_size = os.path.getsize(csv_path)
            row_count = len(df)
            column_count = len(df.columns)
            
            # Create dataset metadata
            dataset_info = {
                "file_path": csv_path,
                "file_name": os.path.basename(csv_path),
                "file_size_bytes": file_size,
                "row_count": row_count,
                "column_count": column_count,
                "columns": list(df.columns),
                "profiling_timestamp": datetime.now().isoformat()
            }
            
            # Start building the profile
            profile = {
                "dataset_info": dataset_info,
                "column_profiles": {},
                "profiling_summary": {},
                "operation_log": self.operation_log
            }
            
            # Profile numeric columns
            self.logger.info("Profiling numeric columns...")
            numeric_profiles = RobustNumericProfiler.profile_dataframe(df)
            
            # Add numeric profiles to the full profile
            for col, num_profile in numeric_profiles.items():
                profile["column_profiles"][col] = {
                    "type": "numeric",
                    "profile": num_profile
                }
            
            # Calculate summary
            missing_cells = sum(prof["profile"].get("null_count", 0) + 
                               prof["profile"].get("invalid_count", 0) 
                               for prof in profile["column_profiles"].values())
            
            total_cells = row_count * column_count
            missing_cells_pct = (missing_cells / total_cells * 100) if total_cells > 0 else 0
            
            profile["profiling_summary"] = {
                "total_rows": row_count,
                "total_columns": column_count,
                "numeric_columns": len(numeric_profiles),
                "missing_cells": missing_cells,
                "missing_cells_percent": missing_cells_pct,
                "completeness": 100 - missing_cells_pct
            }
            
            return profile
            
        except Exception as e:
            self.logger.error(f"Failed to profile CSV {csv_path}: {str(e)}", exc_info=True)
            return {
                "error": str(e),
                "file_path": csv_path,
                "operation_log": self.operation_log
            }


# Testing code
def test_with_problematic_csv():
    """Test the profiler with a CSV containing mixed types."""
    # Create a test CSV with mixed types
    test_csv_path = "test_mixed_types.csv"
    
    try:
        # Create test data with intentional type inconsistencies
        test_df = pd.DataFrame({
            'numeric_clean': [1, 2, 3, 4, 5],
            'numeric_with_string': [10, 20, 'abc', 40, 50],  # Contains a string
            'numeric_with_null': [100, None, 300, 400, 500],  # Contains null
            'mixed_types': [1, '2', 3.5, 'four', None],  # Highly mixed
            'mostly_strings': ['apple', 'banana', '12345', 'orange', 'grape'],
            'dates_with_error': ['2023-01-01', '2023-02-01', 'not-a-date', '2023-04-01', '2023-05-01']
        })
        
        # Save to CSV
        test_df.to_csv(test_csv_path, index=False)
        print(f"Created test CSV at {test_csv_path}")
        
        # Profile the test CSV
        profiler = RobustDatasetProfiler()
        profile = profiler.profile_csv(test_csv_path)
        
        # Print profiling results
        print("\n=== DATASET INFO ===")
        print(f"Rows: {profile['dataset_info']['row_count']}")
        print(f"Columns: {profile['dataset_info']['column_count']}")
        
        print("\n=== COLUMN PROFILES ===")
        for col, data in profile['column_profiles'].items():
            print(f"\nColumn: {col} (Type: {data['type']})")
            
            # Print important numeric metrics
            col_profile = data['profile']
            print(f"  - Count: {col_profile.get('count')}")
            print(f"  - Nulls: {col_profile.get('null_count')} ({col_profile.get('null_percent', 0):.1f}%)")
            
            if 'invalid_count' in col_profile and col_profile['invalid_count'] > 0:
                print(f"  - Invalid values: {col_profile['invalid_count']} "
                      f"({col_profile['invalid_percent']:.1f}%)")
                print(f"  - Sample invalid values: {col_profile['sample_invalid_values']}")
            
            if 'mean' in col_profile:
                print(f"  - Mean: {col_profile['mean']}")
                print(f"  - Min/Max: {col_profile.get('min')} / {col_profile.get('max')}")
            
        print("\n=== SUMMARY ===")
        print(f"Completeness: {profile['profiling_summary']['completeness']:.1f}%")
        print(f"Missing cells: {profile['profiling_summary']['missing_cells']} "
              f"({profile['profiling_summary']['missing_cells_percent']:.1f}%)")
        
        return profile
        
    except Exception as e:
        print(f"Test error: {str(e)}")
    finally:
        # Clean up
        if os.path.exists(test_csv_path):
            # Uncomment to keep test file: os.remove(test_csv_path)
            pass


if __name__ == "__main__":
    # Run the test
    test_with_problematic_csv()