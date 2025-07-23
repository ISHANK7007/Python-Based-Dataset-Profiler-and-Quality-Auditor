import numpy as np
import pandas as pd
from typing import Dict

def calculate_running_stats(df: pd.DataFrame, column: str) -> Dict[str, float]:
    """Calculates count, mean, std, min, and max using pandas."""
    series = df[column].dropna()
    return {
        "count": int(series.count()),
        "mean": float(series.mean()),
        "std": float(series.std()),
        "min": float(series.min()),
        "max": float(series.max())
    }

def reservoir_sample(df: pd.DataFrame, column: str, sample_size: int = 10000) -> pd.Series:
    """Returns a uniform random sample from the column."""
    series = df[column].dropna()
    if len(series) <= sample_size:
        return series
    return series.sample(n=sample_size, random_state=42)

def calculate_quantiles(sample: pd.Series) -> Dict[float, float]:
    """Calculates median, Q1, and Q3 from the sample."""
    return {
        0.25: float(sample.quantile(0.25)),
        0.5: float(sample.median()),
        0.75: float(sample.quantile(0.75)),
    }

def profile_numeric_column_exact_chunked(df: pd.DataFrame, column: str) -> Dict[str, float]:
    """Placeholder: assumes exact chunk-based profiling logic is defined elsewhere."""
    # You should replace this with your actual chunking logic or call from another file.
    series = df[column].dropna()
    return {
        "count": int(series.count()),
        "mean": float(series.mean()),
        "std": float(series.std()),
        "min": float(series.min()),
        "max": float(series.max()),
        "median": float(series.median()),
        "q1": float(series.quantile(0.25)),
        "q3": float(series.quantile(0.75)),
        "distribution": "exact",
        "sample_size": len(series)
    }

def profile_numeric_column_optimized(df: pd.DataFrame, column: str, total_rows: int) -> Dict[str, float]:
    """Optimized numeric column profiling for large datasets."""
    
    if total_rows < 100000:
        return profile_numeric_column_exact_chunked(df, column)
    
    # Use hybrid approximate profiling for large datasets
    running_stats = calculate_running_stats(df, column)
    sample = reservoir_sample(df, column, 10000)
    quantiles = calculate_quantiles(sample)
    
    return {
        "count": running_stats["count"],
        "mean": running_stats["mean"],
        "std": running_stats["std"],
        "min": running_stats["min"],
        "max": running_stats["max"],
        "median": quantiles[0.5],
        "q1": quantiles[0.25],
        "q3": quantiles[0.75],
        "distribution": "approximate",
        "sample_size": len(sample)
    }
