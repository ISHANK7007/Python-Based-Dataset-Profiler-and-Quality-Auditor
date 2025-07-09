import pandas as pd
from typing import Optional, Dict, Any
import numpy as np

def profile_categorical_exact_chunked(df: pd.DataFrame, column: str) -> Dict[str, Any]:
    """Exact frequency count for low cardinality categorical column."""
    series = df[column].dropna()
    value_counts = series.value_counts()
    return {
        "method": "exact_chunked",
        "count": int(series.count()),
        "unique_count": int(series.nunique()),
        "top_categories": value_counts.head(10).to_dict()
    }

def profile_categorical_cms(df: pd.DataFrame, column: str) -> Dict[str, Any]:
    """Approximate profiling using count-min sketch (simulated)."""
    # NOTE: This is a simulated placeholder
    series = df[column].dropna()
    sample = series.sample(n=min(10000, len(series)), random_state=42)
    approx_counts = sample.value_counts().to_dict()
    return {
        "method": "cms",
        "approximate": True,
        "sample_size": len(sample),
        "top_categories": dict(sorted(approx_counts.items(), key=lambda x: x[1], reverse=True)[:10])
    }

def profile_categorical_sampled(df: pd.DataFrame, column: str, sample_size: int) -> Dict[str, Any]:
    """Sample-based profiling with correction for high cardinality."""
    series = df[column].dropna()
    sample = series.sample(n=min(sample_size, len(series)), random_state=42)
    value_counts = sample.value_counts().to_dict()
    return {
        "method": "sampled",
        "sample_size": len(sample),
        "top_categories": dict(sorted(value_counts.items(), key=lambda x: x[1], reverse=True)[:10])
    }

def profile_categorical_column_optimized(df: pd.DataFrame,
                                         column: str,
                                         total_rows: int,
                                         cardinality_estimate: Optional[float] = None) -> Dict[str, Any]:
    """Optimized categorical column profiling for large datasets."""

    # Estimate cardinality from sample if not provided
    if cardinality_estimate is None:
        sample = df[column].dropna().sample(min(5000, total_rows), random_state=42)
        if len(sample) == 0:
            cardinality_estimate = 0
        else:
            cardinality_estimate = sample.nunique() / len(sample) * total_rows

    if cardinality_estimate < 1000:
        return profile_categorical_exact_chunked(df, column)
    elif cardinality_estimate < 100000:
        return profile_categorical_cms(df, column)
    else:
        sample_size = min(50000, max(total_rows // 5, 10000))
        return profile_categorical_sampled(df, column, sample_size)
