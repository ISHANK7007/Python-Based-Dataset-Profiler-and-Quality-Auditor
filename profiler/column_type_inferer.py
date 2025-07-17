from typing import Dict, List, Any, Optional, Union, Set, Tuple
import pandas as pd
import numpy as np
import re
from datetime import datetime
import dateutil.parser
from enum import Enum
import logging

logger = logging.getLogger("dataset_profiler")


class DataType(Enum):
    """Enum representing inferred data types with more granularity than pandas dtypes."""
    UNKNOWN = "unknown"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    DATETIME = "datetime"
    DATE = "date"
    TIME = "time"
    STRING = "string"
    CATEGORICAL = "categorical"
    EMAIL = "email"
    URL = "url"
    IP_ADDRESS = "ip_address"
    PHONE_NUMBER = "phone_number"
    POSTAL_CODE = "postal_code"
    JSON = "json"
    BINARY = "binary"


class ColumnTypeInferer:
    """
    Enhanced column type inference system that combines pandas' type detection
    with custom logic for improved accuracy.
    """
    
    def __init__(self, 
                 sample_size: int = 1000,
                 confidence_threshold: float = 0.7,
                 strict_boolean_values: bool = False,
                 detect_semantic_types: bool = True):
        """
        Initialize the type inferer with configuration options.
        
        Args:
            sample_size: Number of non-null values to sample for inference
            confidence_threshold: Minimum confidence required for type assignment
            strict_boolean_values: If True, only recognize standard boolean values
            detect_semantic_types: Whether to detect specialized string types (email, URL, etc.)
        """
        self.sample_size = sample_size
        self.confidence_threshold = confidence_threshold
        self.strict_boolean_values = strict_boolean_values
        self.detect_semantic_types = detect_semantic_types
        
        # Regular expressions for type detection
        self._compile_regex_patterns()
        
        # Lists of recognized values for flexible type detection
        self._init_recognition_lists()
    
    def _compile_regex_patterns(self):
        """Compile regex patterns for type detection."""
        # Date/time patterns
        self.datetime_patterns = [
            # ISO format: 2023-01-30T10:30:45
            re.compile(r'^\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:?\d{2})?$'),
            # US format: MM/DD/YYYY
            re.compile(r'^(0?[1-9]|1[0-2])[-/](0?[1-9]|[12]\d|3[01])[-/](19|20)\d{2}$'),
            # European format: DD/MM/YYYY
            re.compile(r'^(0?[1-9]|[12]\d|3[01])[-/](0?[1-9]|1[0-2])[-/](19|20)\d{2}$'),
            # Common datetime: YYYY-MM-DD HH:MM:SS
            re.compile(r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}(?:\.\d+)?$'),
        ]
        
        self.date_patterns = [
            # ISO date: YYYY-MM-DD
            re.compile(r'^\d{4}-\d{2}-\d{2}$'),
            # US date without century: MM/DD/YY
            re.compile(r'^(0?[1-9]|1[0-2])[-/](0?[1-9]|[12]\d|3[01])[-/]\d{2}$'),
        ]
        
        self.time_patterns = [
            # HH:MM:SS
            re.compile(r'^\d{2}:\d{2}:\d{2}(?:\.\d+)?$'),
            # HH:MM
            re.compile(r'^\d{2}:\d{2}$'),
            # HH:MM AM/PM
            re.compile(r'^\d{1,2}:\d{2}\s*[AP]M$', re.IGNORECASE),
        ]
        
        # Special string types
        self.email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        self.url_pattern = re.compile(r'^(https?|ftp)://[^\s/$.?#].[^\s]*$|^www\.[^\s/$.?#].[^\s]*$')
        self.ip_pattern = re.compile(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$')
        self.json_pattern = re.compile(r'^\s*[\{\[].*[\}\]]\s*$')
        
    def _init_recognition_lists(self):
        """Initialize lists of recognized values for flexible type detection."""
        # Boolean recognition lists (for non-strict mode)
        self.true_values = [
            'true', 'yes', 'y', 't', '1', 1, True, 
            'on', 'enabled', 'enable', 'active'
        ]
        self.false_values = [
            'false', 'no', 'n', 'f', '0', 0, False,
            'off', 'disabled', 'disable', 'inactive'
        ]
    
    def infer_column_type(self, series: pd.Series, sample_size: Optional[int] = None) -> Dict[str, Any]:
        """
        Infer the data type of a column with detailed confidence metrics.
        
        Args:
            series: Pandas Series representing a column
            sample_size: Optional override for sample size
            
        Returns:
            Dictionary containing inferred type information and confidence metrics
        """
        if series.empty:
            return {
                "inferred_type": DataType.UNKNOWN.value,
                "pandas_dtype": str(series.dtype),
                "confidence": 0.0,
                "reason": "Empty column"
            }
        
        # Get a sample of non-null values for analysis
        non_null = series.dropna()
        if non_null.empty:
            return {
                "inferred_type": DataType.UNKNOWN.value,
                "pandas_dtype": str(series.dtype),
                "confidence": 0.0,
                "reason": "All values are null"
            }
        
        sample_size = sample_size or self.sample_size
        sample = non_null.sample(min(sample_size, len(non_null))) if len(non_null) > sample_size else non_null
        
        # Check pandas dtype first
        pandas_dtype = str(series.dtype)
        
        # Start with pandas' inference as a base
        if pd.api.types.is_integer_dtype(series):
            return {
                "inferred_type": DataType.INTEGER.value,
                "pandas_dtype": pandas_dtype,
                "confidence": 1.0,
                "reason": "Pandas integer dtype"
            }
        elif pd.api.types.is_float_dtype(series):
            return {
                "inferred_type": DataType.FLOAT.value,
                "pandas_dtype": pandas_dtype,
                "confidence": 1.0,
                "reason": "Pandas float dtype"
            }
        elif pd.api.types.is_bool_dtype(series):
            return {
                "inferred_type": DataType.BOOLEAN.value,
                "pandas_dtype": pandas_dtype,
                "confidence": 1.0,
                "reason": "Pandas boolean dtype"
            }
        elif pd.api.types.is_datetime64_dtype(series):
            return {
                "inferred_type": DataType.DATETIME.value,
                "pandas_dtype": pandas_dtype,
                "confidence": 1.0,
                "reason": "Pandas datetime dtype"
            }
        
        # For object or category dtypes, we need deeper inspection
        # Convert sample to strings for consistent analysis
        str_sample = sample.astype(str)
        
        # Try each type detection in order of specificity
        type_checks = [
            self._check_boolean,
            self._check_integer,
            self._check_float,
            self._check_datetime,
            self._check_date,
            self._check_time
        ]
        
        results = []
        for check_func in type_checks:
            result = check_func(str_sample)
            if result['match_ratio'] > 0:
                results.append(result)
        
        # Check semantic string types if enabled
        if self.detect_semantic_types:
            for check_func in [self._check_email, self._check_url, self._check_ip_address, 
                              self._check_json]:
                result = check_func(str_sample)
                if result['match_ratio'] > 0:
                    results.append(result)
        
        # Sort by match ratio in descending order
        results.sort(key=lambda x: x['match_ratio'], reverse=True)
        
        # If nothing matched well, it's a string or categorical
        if not results or results[0]['match_ratio'] < self.confidence_threshold:
            # Check if likely categorical
            unique_ratio = len(sample.unique()) / len(sample)
            if unique_ratio < 0.1 and len(sample) >= 20:  # Heuristic for categorical detection
                return {
                    "inferred_type": DataType.CATEGORICAL.value,
                    "pandas_dtype": pandas_dtype,
                    "confidence": min(1.0, 1.0 - unique_ratio),
                    "reason": f"Low unique ratio ({unique_ratio:.2f})",
                    "unique_ratio": unique_ratio,
                    "unique_count": len(sample.unique())
                }
            else:
                return {
                    "inferred_type": DataType.STRING.value,
                    "pandas_dtype": pandas_dtype,
                    "confidence": 0.5,  # Default confidence for string
                    "reason": "No specific type detected with confidence"
                }
        
        # Return the best match
        best_match = results[0]
        return {
            "inferred_type": best_match['type'],
            "pandas_dtype": pandas_dtype,
            "confidence": best_match['match_ratio'],
            "reason": best_match['reason'],
            "match_count": best_match['match_count'],
            "total_tested": best_match['total_tested']
        }
    
    def _check_boolean(self, sample: pd.Series) -> Dict[str, Any]:
        """Check if values are boolean-like."""
        match_count = 0
        total = len(sample)
        
        if self.strict_boolean_values:
            # Strict mode - only accept true/false variations
            for val in sample:
                val_lower = val.lower() if isinstance(val, str) else val
                if val_lower in [str(x).lower() for x in self.true_values + self.false_values]:
                    match_count += 1
        else:
            # Flexible mode - accept anything that pandas to_numeric doesn't handle 
            # but converts cleanly to bool
            for val in sample:
                try:
                    val_lower = val.lower() if isinstance(val, str) else val
                    if val_lower in [str(x).lower() for x in self.true_values]:
                        match_count += 1
                    elif val_lower in [str(x).lower() for x in self.false_values]:
                        match_count += 1
                except:
                    pass
        
        match_ratio = match_count / total if total > 0 else 0
        return {
            'type': DataType.BOOLEAN.value,
            'match_count': match_count,
            'total_tested': total,
            'match_ratio': match_ratio,
            'reason': f"{match_count}/{total} values match boolean pattern"
        }
    
    def _check_integer(self, sample: pd.Series) -> Dict[str, Any]:
        """Check if values are integers."""
        match_count = 0
        total = len(sample)
        
        for val in sample:
            # Skip empty strings
            if val == '':
                total -= 1
                continue
                
            try:
                # Check if it's an integer without decimal
                num = float(val)
                if num.is_integer():
                    match_count += 1
            except:
                pass
        
        match_ratio = match_count / total if total > 0 else 0
        return {
            'type': DataType.INTEGER.value,
            'match_count': match_count,
            'total_tested': total,
            'match_ratio': match_ratio,
            'reason': f"{match_count}/{total} values are integers"
        }
    
    def _check_float(self, sample: pd.Series) -> Dict[str, Any]:
        """Check if values are floating point numbers."""
        match_count = 0
        total = len(sample)
        
        for val in sample:
            # Skip empty strings
            if val == '':
                total -= 1
                continue
                
            try:
                # Check if it's a valid float
                float(val)
                match_count += 1
            except:
                pass
        
        match_ratio = match_count / total if total > 0 else 0
        return {
            'type': DataType.FLOAT.value,
            'match_count': match_count,
            'total_tested': total,
            'match_ratio': match_ratio,
            'reason': f"{match_count}/{total} values are floating point"
        }
    
    def _check_datetime(self, sample: pd.Series) -> Dict[str, Any]:
        """Check if values are datetime."""
        match_count = 0
        total = len(sample)
        
        for val in sample:
            # Skip empty strings
            if val == '':
                total -= 1
                continue
                
            # Try regex patterns first for speed
            pattern_match = any(pattern.match(val) for pattern in self.datetime_patterns)
            
            if pattern_match:
                match_count += 1
            else:
                # Fall back to dateutil parser for complex cases
                try:
                    dateutil.parser.parse(val)
                    match_count += 1
                except:
                    pass
        
        match_ratio = match_count / total if total > 0 else 0
        return {
            'type': DataType.DATETIME.value,
            'match_count': match_count,
            'total_tested': total,
            'match_ratio': match_ratio,
            'reason': f"{match_count}/{total} values match datetime pattern"
        }
    
    def _check_date(self, sample: pd.Series) -> Dict[str, Any]:
        """Check if values are dates without time component."""
        match_count = 0
        total = len(sample)
        
        for val in sample:
            # Skip empty strings
            if val == '':
                total -= 1
                continue
                
            # Try regex patterns
            if any(pattern.match(val) for pattern in self.date_patterns):
                match_count += 1
        
        match_ratio = match_count / total if total > 0 else 0
        return {
            'type': DataType.DATE.value,
            'match_count': match_count,
            'total_tested': total,
            'match_ratio': match_ratio,
            'reason': f"{match_count}/{total} values match date pattern"
        }
    
    def _check_time(self, sample: pd.Series) -> Dict[str, Any]:
        """Check if values are times without date component."""
        match_count = 0
        total = len(sample)
        
        for val in sample:
            # Skip empty strings
            if val == '':
                total -= 1
                continue
                
            # Try regex patterns
            if any(pattern.match(val) for pattern in self.time_patterns):
                match_count += 1
        
        match_ratio = match_count / total if total > 0 else 0
        return {
            'type': DataType.TIME.value,
            'match_count': match_count,
            'total_tested': total,
            'match_ratio': match_ratio,
            'reason': f"{match_count}/{total} values match time pattern"
        }
    
    def _check_email(self, sample: pd.Series) -> Dict[str, Any]:
        """Check if values are email addresses."""
        match_count = 0
        total = len(sample)
        
        for val in sample:
            if self.email_pattern.match(val):
                match_count += 1
        
        match_ratio = match_count / total if total > 0 else 0
        return {
            'type': DataType.EMAIL.value,
            'match_count': match_count,
            'total_tested': total,
            'match_ratio': match_ratio,
            'reason': f"{match_count}/{total} values are emails"
        }
    
    def _check_url(self, sample: pd.Series) -> Dict[str, Any]:
        """Check if values are URLs."""
        match_count = 0
        total = len(sample)
        
        for val in sample:
            if self.url_pattern.match(val):
                match_count += 1
        
        match_ratio = match_count / total if total > 0 else 0
        return {
            'type': DataType.URL.value,
            'match_count': match_count,
            'total_tested': total,
            'match_ratio': match_ratio,
            'reason': f"{match_count}/{total} values are URLs"
        }
    
    def _check_ip_address(self, sample: pd.Series) -> Dict[str, Any]:
        """Check if values are IP addresses."""
        match_count = 0
        total = len(sample)
        
        for val in sample:
            if self.ip_pattern.match(val):
                match_count += 1
        
        match_ratio = match_count / total if total > 0 else 0
        return {
            'type': DataType.IP_ADDRESS.value,
            'match_count': match_count,
            'total_tested': total,
            'match_ratio': match_ratio,
            'reason': f"{match_count}/{total} values are IP addresses"
        }
    
    def _check_json(self, sample: pd.Series) -> Dict[str, Any]:
        """Check if values are JSON strings."""
        match_count = 0
        total = len(sample)
        
        for val in sample:
            if self.json_pattern.match(val):
                # Verify it's valid JSON by trying to parse it
                try:
                    import json
                    json.loads(val)
                    match_count += 1
                except:
                    pass
        
        match_ratio = match_count / total if total > 0 else 0
        return {
            'type': DataType.JSON.value,
            'match_count': match_count,
            'total_tested': total,
            'match_ratio': match_ratio,
            'reason': f"{match_count}/{total} values are valid JSON"
        }
    
    def infer_dataframe_types(self, df: pd.DataFrame, sample_size: Optional[int] = None) -> Dict[str, Dict[str, Any]]:
        """
        Infer types for all columns in a dataframe.
        
        Args:
            df: Pandas DataFrame to profile
            sample_size: Optional sample size for inference
            
        Returns:
            Dictionary mapping column names to their type information
        """
        results = {}
        for col in df.columns:
            try:
                results[col] = self.infer_column_type(df[col], sample_size)
            except Exception as e:
                logger.warning(f"Error inferring type for column '{col}': {str(e)}")
                results[col] = {
                    "inferred_type": DataType.UNKNOWN.value,
                    "pandas_dtype": str(df[col].dtype),
                    "confidence": 0.0,
                    "error": str(e)
                }
        
        return results
    
    def suggest_type_conversion(self, df: pd.DataFrame, type_info: Optional[Dict[str, Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Suggest type conversions for a dataframe based on inferred types.
        
        Args:
            df: Pandas DataFrame to analyze
            type_info: Optional pre-computed type information
            
        Returns:
            Dictionary with conversion suggestions
        """
        if type_info is None:
            type_info = self.infer_dataframe_types(df)
            
        conversion_map = {}
        
        for col, info in type_info.items():
            inferred_type = info.get('inferred_type')
            confidence = info.get('confidence', 0)
            
            # Only suggest conversions with good confidence
            if confidence >= self.confidence_threshold:
                # Map our types to pandas types
                if inferred_type == DataType.INTEGER.value:
                    conversion_map[col] = 'int64'
                elif inferred_type == DataType.FLOAT.value:
                    conversion_map[col] = 'float64'
                elif inferred_type == DataType.BOOLEAN.value:
                    conversion_map[col] = 'bool'
                elif inferred_type == DataType.DATETIME.value or inferred_type == DataType.DATE.value:
                    conversion_map[col] = 'datetime64[ns]'
                elif inferred_type == DataType.CATEGORICAL.value:
                    conversion_map[col] = 'category'
        
        return {
            'conversion_map': conversion_map,
            'code_snippet': f"df = df.astype({repr(conversion_map)})"
        }


# Example usage
def test_type_inference():
    """Test the type inference system."""
    # Create a test dataframe with various types
    data = {
        "int_column": [1, 2, 3, 4, 5],
        "float_column": [1.1, 2.2, 3.3, 4.4, 5.5],
        "bool_column": [True, False, True, False, True],
        "string_column": ["apple", "banana", "cherry", "date", "elderberry"],
        "mixed_int_string": ["1", "2", "three", "4", "5"],
        "date_iso": ["2023-01-01", "2023-01-02", "2023-01-03", "2023-01-04", "2023-01-05"],
        "date_us": ["01/01/2023", "01/02/2023", "01/03/2023", "01/04/2023", "01/05/2023"],
        "datetime_iso": ["2023-01-01T12:00:00", "2023-01-02T12:00:00", 
                        "2023-01-03T12:00:00", "2023-01-04T12:00:00", "2023-01-05T12:00:00"],
        "time_column": ["12:30:45", "13:30:45", "14:30:45", "15:30:45", "16:30:45"],
        "email_column": ["user1@example.com", "user2@example.com", 
                        "user3@example.com", "user4@example.com", "user5@example.com"],
        "bool_text": ["true", "false", "True", "False", "yes"],
        "categorical": ["A", "B", "A", "C", "B"]
    }
    
    df = pd.DataFrame(data)
    
    # Create the type inferer
    inferer = ColumnTypeInferer()
    
    # Infer types for the dataframe
    type_info = inferer.infer_dataframe_types(df)
    
    # Print results
    print("\n=== TYPE INFERENCE RESULTS ===")
    for col, info in type_info.items():
        print(f"\nColumn: {col}")
        print(f"  Inferred Type: {info['inferred_type']}")
        print(f"  Pandas Type: {info['pandas_dtype']}")
        print(f"  Confidence: {info.get('confidence', 0):.2f}")
        print(f"  Reason: {info.get('reason', 'N/A')}")
    
    # Get type conversion suggestions
    conversion_suggestions = inferer.suggest_type_conversion(df, type_info)
    
    print("\n=== TYPE CONVERSION SUGGESTIONS ===")
    print(conversion_suggestions['code_snippet'])
    
    return type_info

def detect_column_type(series: pd.Series) -> DataType:
    """
    Functional wrapper for ColumnTypeInferer to integrate with profiler system.
    Returns a DataType enum directly.
    """
    inferer = ColumnTypeInferer()
    result = inferer.infer_column_type(series)
    return DataType(result["inferred_type"])

if __name__ == "__main__":
    test_type_inference()