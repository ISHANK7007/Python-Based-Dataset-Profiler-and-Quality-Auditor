import pandas as pd
import numpy as np
import re
import base64
from typing import List, Dict, Any, Optional, Union, Set, Tuple
import statistics
import logging

logger = logging.getLogger("dataset_profiler")


class ColumnExclusionHeuristics:
    """
    Provides heuristics to determine which columns should be excluded from detailed profiling.
    Uses various metrics to identify columns that are likely to be free text, binary data, or otherwise
    problematic for standard profiling techniques.
    """
    
    def __init__(self,
                max_string_length: int = 1000,
                max_unique_ratio: float = 0.9,
                max_avg_token_count: int = 50,
                max_storage_size_mb: float = 10.0,
                base64_detection_threshold: float = 0.8,
                hex_detection_threshold: float = 0.9,
                uuid_detection_threshold: float = 0.7,
                json_detection_threshold: float = 0.7):
        """
        Initialize the heuristics configuration.
        
        Args:
            max_string_length: Maximum average string length before flagging as potential text blob
            max_unique_ratio: Maximum ratio of unique values to total values (for high cardinality detection)
            max_avg_token_count: Maximum average whitespace-delimited token count for normal text fields
            max_storage_size_mb: Maximum column storage size in MB before recommending exclusion
            base64_detection_threshold: Threshold for detecting base64 encoded content
            hex_detection_threshold: Threshold for detecting hexadecimal content
            uuid_detection_threshold: Threshold for detecting UUID strings
            json_detection_threshold: Threshold for detecting JSON content
        """
        self.max_string_length = max_string_length
        self.max_unique_ratio = max_unique_ratio
        self.max_avg_token_count = max_avg_token_count
        self.max_storage_size_mb = max_storage_size_mb
        self.base64_detection_threshold = base64_detection_threshold
        self.hex_detection_threshold = hex_detection_threshold
        self.uuid_detection_threshold = uuid_detection_threshold
        self.json_detection_threshold = json_detection_threshold
        
        # Compile regex patterns
        self.base64_pattern = re.compile(r'^[A-Za-z0-9+/]+={0,2}$')
        self.hex_pattern = re.compile(r'^[0-9a-fA-F]+$')
        self.uuid_pattern = re.compile(
            r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', 
            re.IGNORECASE
        )
        self.json_pattern = re.compile(r'^\s*[\{\[].*[\}\]]\s*$')
    
    def analyze_column(self, series: pd.Series, sample_size: int = 500) -> Dict[str, Any]:
        """
        Analyze a column to determine if it should be excluded from detailed profiling.
        
        Args:
            series: The pandas Series to analyze
            sample_size: Number of non-null values to sample for analysis
            
        Returns:
            Dictionary with analysis results and recommendation
        """
        column_name = series.name or "unnamed_column"
        result = {
            "column_name": column_name,
            "exclude": False,
            "reasons": [],
            "content_type": "unknown",
            "metrics": {}
        }
        
        # Skip analysis for empty columns
        if series.empty or series.isna().all():
            return result
        
        # Get sample of non-null values
        valid_values = series.dropna()
        sample = valid_values.sample(min(sample_size, len(valid_values))) if len(valid_values) > sample_size else valid_values
        
        # Check data type
        dtype_name = str(series.dtype)
        result["metrics"]["dtype"] = dtype_name
        
        # Different analysis based on data type
        if pd.api.types.is_numeric_dtype(series):
            # For numeric columns, check if it might be a unique identifier
            unique_ratio = series.nunique() / len(series.dropna()) if len(series.dropna()) > 0 else 0
            result["metrics"]["unique_ratio"] = unique_ratio
            
            if unique_ratio > self.max_unique_ratio and len(series) > 100:
                result["exclude"] = True
                result["reasons"].append("High cardinality numeric column likely to be an ID")
                result["content_type"] = "numeric_id"
        
        elif pd.api.types.is_string_dtype(series) or pd.api.types.is_object_dtype(series):
            # Convert to string for analysis, handling non-string objects
            string_sample = sample.astype(str)
            
            # Calculate string lengths
            string_lengths = string_sample.str.len()
            avg_length = string_lengths.mean() if not string_lengths.empty else 0
            max_length = string_lengths.max() if not string_lengths.empty else 0
            
            result["metrics"]["avg_string_length"] = avg_length
            result["metrics"]["max_string_length"] = max_length
            
            # Calculate unique ratio
            unique_ratio = series.nunique() / len(series.dropna()) if len(series.dropna()) > 0 else 0
            result["metrics"]["unique_ratio"] = unique_ratio
            
            # Check for excessive length
            if avg_length > self.max_string_length:
                result["exclude"] = True
                result["reasons"].append(f"Long string content (avg length: {avg_length:.1f})")
                result["content_type"] = "long_text"
            
            # Calculate token counts (rough word count)
            if avg_length > 0:
                token_counts = string_sample.str.split().str.len()
                avg_tokens = token_counts.mean() if not token_counts.empty else 0
                result["metrics"]["avg_token_count"] = avg_tokens
                
                if avg_tokens > self.max_avg_token_count:
                    result["exclude"] = True
                    result["reasons"].append(f"Multi-token text field (avg tokens: {avg_tokens:.1f})")
                    result["content_type"] = "free_text"
            
            # Detect common encodings and formats
            encoding_checks = self._detect_encodings(string_sample)
            result["metrics"].update(encoding_checks)
            
            if encoding_checks.get("likely_base64", False):
                result["exclude"] = True
                result["reasons"].append("Likely base64 encoded content")
                result["content_type"] = "base64"
            
            if encoding_checks.get("likely_json", False):
                result["exclude"] = True
                result["reasons"].append("Likely JSON content")
                result["content_type"] = "json"
                
            if encoding_checks.get("likely_hex", False):
                result["exclude"] = True
                result["reasons"].append("Likely hexadecimal content")
                result["content_type"] = "hex"
                
            if encoding_checks.get("likely_uuid", False):
                # UUIDs we don't always exclude, but flag them as IDs
                result["content_type"] = "uuid"
                if unique_ratio > self.max_unique_ratio:
                    result["exclude"] = True
                    result["reasons"].append("High cardinality UUID column")
            
            # Handle high cardinality string columns
            if unique_ratio > self.max_unique_ratio and len(series) > 100:
                # Only exclude if not already categorized
                if not result["reasons"]:
                    result["exclude"] = True
                    result["reasons"].append("High cardinality string column")
                    result["content_type"] = "high_cardinality"
        
        # Note: Consider checking estimated memory size of the column
        try:
            memory_usage = series.memory_usage(deep=True) / (1024 * 1024)  # MB
            result["metrics"]["memory_usage_mb"] = memory_usage
            
            if memory_usage > self.max_storage_size_mb:
                result["exclude"] = True
                result["reasons"].append(f"Large memory footprint: {memory_usage:.2f} MB")
        except Exception as e:
            logger.warning(f"Couldn't calculate memory usage for column {column_name}: {str(e)}")
        
        return result
    
    def _detect_encodings(self, string_sample: pd.Series) -> Dict[str, Any]:
        """
        Detect if the content matches common encodings or formats.
        
        Args:
            string_sample: Series of string values to check
            
        Returns:
            Dictionary with detection results
        """
        results = {}
        
        # Only perform checks on non-empty strings
        non_empty = string_sample[string_sample.str.len() > 4]
        if len(non_empty) == 0:
            return results
        
        # Check for base64 encoded content
        base64_matches = non_empty.apply(lambda x: bool(self.base64_pattern.match(str(x))))
        base64_ratio = base64_matches.mean() if not base64_matches.empty else 0
        results["base64_ratio"] = base64_ratio
        results["likely_base64"] = base64_ratio > self.base64_detection_threshold
        
        # Try to decode a few samples as base64 if likely
        if results["likely_base64"]:
            try:
                # Sample a few values and see if they decode properly
                sample_values = non_empty[base64_matches].sample(min(5, len(non_empty[base64_matches])))
                successful_decodes = 0
                
                for value in sample_values:
                    try:
                        # Add padding if needed
                        padded_value = value + '=' * (4 - len(value) % 4)
                        decoded = base64.b64decode(padded_value)
                        # If we're here, it decoded successfully
                        successful_decodes += 1
                    except:
                        pass
                
                # If none decoded successfully, it's probably not base64 despite matching pattern
                if successful_decodes == 0:
                    results["likely_base64"] = False
            except Exception as e:
                logger.debug(f"Error in base64 decode test: {str(e)}")
        
        # Check for hexadecimal content
        hex_matches = non_empty.apply(lambda x: bool(self.hex_pattern.match(str(x))))
        hex_ratio = hex_matches.mean() if not hex_matches.empty else 0
        results["hex_ratio"] = hex_ratio
        results["likely_hex"] = hex_ratio > self.hex_detection_threshold
        
        # Check for UUID strings
        uuid_matches = non_empty.apply(lambda x: bool(self.uuid_pattern.match(str(x))))
        uuid_ratio = uuid_matches.mean() if not uuid_matches.empty else 0
        results["uuid_ratio"] = uuid_ratio
        results["likely_uuid"] = uuid_ratio > self.uuid_detection_threshold
        
        # Check for JSON content
        json_matches = non_empty.apply(lambda x: bool(self.json_pattern.match(str(x))))
        json_ratio = json_matches.mean() if not json_matches.empty else 0
        results["json_ratio"] = json_ratio
        results["likely_json"] = json_ratio > self.json_detection_threshold
        
        # If likely JSON, perform additional validation
        if results["likely_json"]:
            try:
                # Sample a few values and see if they parse as JSON
                sample_values = non_empty[json_matches].sample(min(5, len(non_empty[json_matches])))
                successful_parses = 0
                
                import json
                for value in sample_values:
                    try:
                        json.loads(value)
                        successful_parses += 1
                    except:
                        pass
                
                # Update likelihood based on parsing success
                results["likely_json"] = successful_parses > 0
            except Exception as e:
                logger.debug(f"Error in JSON validation: {str(e)}")
        
        return results


class ProfilerConfig:
    """Configuration for the dataset profiler."""
    
    def __init__(self, 
                exclude_large_text: bool = True,
                exclude_binary_data: bool = True,
                exclude_high_cardinality: bool = False,
                text_summarization_only: bool = True,
                max_string_length: int = 1000,
                max_unique_ratio: float = 0.9,
                max_avg_token_count: int = 50,
                max_storage_size_mb: float = 10.0):
        """
        Initialize profiler configuration.
        
        Args:
            exclude_large_text: Whether to skip detailed profiling of large text fields
            exclude_binary_data: Whether to skip binary-like data (base64, hex)
            exclude_high_cardinality: Whether to skip columns with high cardinality
            text_summarization_only: For text columns, only include summary stats rather than skip entirely
            max_string_length: Maximum average string length before flagging as text blob
            max_unique_ratio: Maximum unique value ratio before considering high cardinality
            max_avg_token_count: Maximum average token count for normal text fields
            max_storage_size_mb: Maximum column storage size in MB before recommending exclusion
        """
        self.exclude_large_text = exclude_large_text
        self.exclude_binary_data = exclude_binary_data
        self.exclude_high_cardinality = exclude_high_cardinality
        self.text_summarization_only = text_summarization_only
        
        # Create heuristics instance with configured thresholds
        self.heuristics = ColumnExclusionHeuristics(
            max_string_length=max_string_length,
            max_unique_ratio=max_unique_ratio,
            max_avg_token_count=max_avg_token_count,
            max_storage_size_mb=max_storage_size_mb
        )
    
    def should_exclude_column(self, column_analysis: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Determine if a column should be excluded based on analysis and configuration.
        
        Args:
            column_analysis: Analysis results from ColumnExclusionHeuristics
            
        Returns:
            Tuple of (should_exclude, reason_or_empty_string)
        """
        content_type = column_analysis.get("content_type", "unknown")
        
        # Apply configuration rules
        if content_type in ["base64", "hex"] and self.exclude_binary_data:
            return True, f"Binary data excluded: {content_type}"
            
        if content_type in ["long_text", "free_text"] and self.exclude_large_text:
            if self.text_summarization_only:
                return False, f"Text summarization only: {content_type}"
            return True, f"Large text excluded: {content_type}"
            
        if content_type in ["high_cardinality", "numeric_id", "uuid"] and self.exclude_high_cardinality:
            return True, f"High cardinality excluded: {content_type}"
            
        if content_type == "json":
            return True, "JSON content excluded"
        
        # If the analysis recommends exclusion but our rules don't specifically cover it
        if column_analysis.get("exclude", False):
            reasons = ", ".join(column_analysis.get("reasons", ["unspecified"]))
            return True, f"Excluded by heuristics: {reasons}"
            
        return False, ""


class RobustDatasetProfiler:
    """Enhanced dataset profiler with column exclusion capabilities."""
    
    def __init__(self, config: Optional[ProfilerConfig] = None):
        """
        Initialize the enhanced profiler.
        
        Args:
            config: Configuration for the profiler
        """
        self.config = config or ProfilerConfig()
        self.logger = logging.getLogger("dataset_profiler")
        self.exclusion_heuristics = self.config.heuristics
        
    def analyze_dataframe_columns(self, df: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
        """
        Analyze dataframe columns to determine which ones should be excluded from detailed profiling.
        
        Args:
            df: Pandas DataFrame to analyze
            
        Returns:
            Dictionary mapping column names to their analysis results
        """
        results = {}
        
        for col in df.columns:
            try:
                analysis = self.exclusion_heuristics.analyze_column(df[col])
                should_exclude, reason = self.config.should_exclude_column(analysis)
                
                # Override the exclusion flag based on configuration
                analysis["exclude"] = should_exclude
                if reason and reason not in analysis.get("reasons", []):
                    if "reasons" not in analysis:
                        analysis["reasons"] = []
                    analysis["reasons"].append(reason)
                    
                results[col] = analysis
                
                if should_exclude:
                    self.logger.info(
                        f"Column '{col}' will be excluded from detailed profiling: {reason}. "
                        f"Content type: {analysis.get('content_type', 'unknown')}"
                    )
            except Exception as e:
                self.logger.warning(f"Error analyzing column '{col}': {str(e)}")
                results[col] = {
                    "column_name": col,
                    "exclude": False,
                    "error": str(e),
                    "content_type": "error"
                }
        
        return results

    def profile_dataframe(self, df: pd.DataFrame, **kwargs) -> Dict[str, Any]:
        """
        Profile a DataFrame with automatic column exclusion.
        
        Args:
            df: The DataFrame to profile
            **kwargs: Additional profiling parameters
            
        Returns:
            Dictionary with profiling results
        """
        # First, analyze columns for exclusion
        column_analysis = self.analyze_dataframe_columns(df)
        
        # Divide columns into excluded and included
        excluded_columns = [col for col, analysis in column_analysis.items() 
                          if analysis.get("exclude", False)]
        
        included_columns = [col for col in df.columns if col not in excluded_columns]
        
        # Create summary of exclusions
        exclusion_summary = {
            "excluded_column_count": len(excluded_columns),
            "excluded_columns": excluded_columns,
            "excluded_column_details": {
                col: {
                    "content_type": column_analysis[col].get("content_type", "unknown"),
                    "reasons": column_analysis[col].get("reasons", []),
                    "metrics": column_analysis[col].get("metrics", {})
                } 
                for col in excluded_columns
            },
            "included_column_count": len(included_columns),
            "included_columns": included_columns
        }
        
        # For text columns that need summarization only
        text_summary_columns = [
            col for col, analysis in column_analysis.items()
            if analysis.get("content_type") in ["long_text", "free_text"] 
            and not analysis.get("exclude", False)
            and self.config.text_summarization_only
        ]
        
        # Profile the included columns normally
        # This would call the existing profiling code, which we'll simulate here
        profile_results = self._profile_columns(df, included_columns, text_summary_columns, **kwargs)
        
        # Add exclusion information to the profile
        profile_results["column_exclusion_info"] = exclusion_summary
        
        return profile_results
    
    def _profile_columns(self, df: pd.DataFrame, 
                        included_columns: List[str], 
                        text_summary_columns: List[str],
                        **kwargs) -> Dict[str, Any]:
        """
        Internal method to profile columns based on their categorization.
        
        This is a placeholder that would call the actual profiling implementations.
        """
        # This is a simplified simulation of what would happen
        result = {
            "dataset_info": {
                "row_count": len(df),
                "column_count": len(df.columns),
                "profiled_column_count": len(included_columns)
            },
            "column_profiles": {}
        }
        
        # Process non-text columns with full profiling
        standard_columns = [col for col in included_columns if col not in text_summary_columns]
        
        # For demo purposes only - this would call actual profilers
        for col in standard_columns:
            result["column_profiles"][col] = {"profiled": "full"}
            
        # Process text columns with summarization only
        for col in text_summary_columns:
            # Create a summary profile instead of detailed profile
            summary_stats = self._summarize_text_column(df[col])
            result["column_profiles"][col] = {
                "profiled": "summary",
                "summary": summary_stats
            }
            
        return result
    
    def _summarize_text_column(self, series: pd.Series) -> Dict[str, Any]:
        """
        Create a lightweight summary for text columns instead of full profiling.
        
        Args:
            series: The text column to summarize
            
        Returns:
            Dictionary with text column summary
        """
        # Drop NA values
        valid_values = series.dropna()
        
        if len(valid_values) == 0:
            return {
                "count": 0,
                "null_count": len(series),
                "null_percent": 100.0
            }
        
        # Convert to strings
        string_values = valid_values.astype(str)
        
        # Calculate basic stats
        char_lengths = string_values.str.len()
        word_counts = string_values.str.split().str.len()
        
        # Sample a few values
        sample_size = min(5, len(string_values))
        samples = string_values.sample(sample_size).tolist()
        
        # Build summary
        summary = {
            "count": len(series),
            "null_count": len(series) - len(valid_values),
            "null_percent": (len(series) - len(valid_values)) / len(series) * 100 if len(series) > 0 else 0,
            "min_length": int(char_lengths.min()) if not char_lengths.empty else 0,
            "max_length": int(char_lengths.max()) if not char_lengths.empty else 0,
            "avg_length": float(char_lengths.mean()) if not char_lengths.empty else 0,
            "min_words": int(word_counts.min()) if not word_counts.empty else 0,
            "max_words": int(word_counts.max()) if not word_counts.empty else 0,
            "avg_words": float(word_counts.mean()) if not word_counts.empty else 0,
            "sample_values": [
                value[:100] + "..." if len(value) > 100 else value
                for value in samples
            ],
            "unique_count": string_values.nunique(),
            "unique_percent": (string_values.nunique() / len(string_values) * 100) if len(string_values) > 0 else 0
        }
        
        return summary


# Example usage
def test_column_exclusion():
    """Test the column exclusion functionality."""
    # Create a test dataframe with problematic columns
    data = {
        # Normal columns
        "numeric_column": [1, 2, 3, 4, 5],
        "category_column": ["A", "B", "C", "A", "B"],
        
        # Problematic columns
        "uuid_column": [
            "123e4567-e89b-12d3-a456-426614174000",
            "123e4567-e89b-12d3-a456-426614174001",
            "123e4567-e89b-12d3-a456-426614174002",
            "123e4567-e89b-12d3-a456-426614174003",
            "123e4567-e89b-12d3-a456-426614174004"
        ],
        "base64_column": [
            "SGVsbG8gV29ybGQ=",  # "Hello World"
            "VGhpcyBpcyBhIHRlc3Q=",  # "This is a test"
            "QW5vdGhlciBzdHJpbmc=",  # "Another string"
            "QmFzZTY0IGVuY29kZWQ=",  # "Base64 encoded"
            "U29tZSBvdGhlciB0ZXh0"   # "Some other text"
        ],
        "long_text_column": [
            "This is a long text that would be problematic for profiling. " * 10,
            "Another lengthy paragraph with many words and characters. " * 10,
            "More text that goes on and on, containing many words. " * 10,
            "Text that would take up significant space in a profile report. " * 10,
            "Free-form text field with lots of content to analyze. " * 10
        ],
        "json_column": [
            '{"name": "John", "age": 30, "city": "New York"}',
            '{"name": "Alice", "age": 25, "city": "Los Angeles"}',
            '{"name": "Bob", "age": 35, "city": "Chicago"}',
            '{"name": "Eva", "age": 28, "city": "Miami"}',
            '{"name": "Mike", "age": 32, "city": "Seattle"}'
        ]
    }
    
    df = pd.DataFrame(data)
    
    # Create the profiler with default config
    profiler = RobustDatasetProfiler()
    
    # Analyze columns
    column_analysis = profiler.analyze_dataframe_columns(df)
    
    # Print results
    print("\n=== RECOMMENDED COLUMN EXCLUSIONS ===")
    for col, analysis in column_analysis.items():
        print(f"\nColumn: {col}")
        print(f"  Content Type: {analysis.get('content_type', 'unknown')}")
        print(f"  Exclude: {analysis.get('exclude', False)}")
        if analysis.get('reasons'):
            print(f"  Reasons: {', '.join(analysis['reasons'])}")
        
        # Print some metrics if available
        if 'metrics' in analysis:
            metrics = analysis['metrics']
            if metrics:
                print("  Metrics:")
                for k, v in metrics.items():
                    if isinstance(v, (float, np.float64)):
                        print(f"    {k}: {v:.2f}")
                    else:
                        print(f"    {k}: {v}")
    
    # Test full profiling workflow
    print("\n=== PROFILING WITH AUTOMATIC EXCLUSION ===")
    profile = profiler.profile_dataframe(df)
    
    # Print exclusion summary
    exclusion_info = profile.get("column_exclusion_info", {})
    print(f"Excluded columns: {exclusion_info.get('excluded_column_count', 0)}")
    print(f"Excluded: {exclusion_info.get('excluded_columns', [])}")
    print(f"\nIncluded columns: {exclusion_info.get('included_column_count', 0)}")
    print(f"Included: {exclusion_info.get('included_columns', [])}")
    
    return profile


if __name__ == "__main__":
    # Run the test
    test_column_exclusion()