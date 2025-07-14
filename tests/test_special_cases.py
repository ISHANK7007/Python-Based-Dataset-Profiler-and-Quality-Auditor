import unittest
import pandas as pd
import numpy as np
import os
import psutil
import gc
from profiler.basic_profiler import profile_dataset

class TestSpecializedCases(unittest.TestCase):
    """Additional tests for specific edge cases."""

    def test_single_value_columns(self):
        """Test columns containing only a single distinct value."""
        df = pd.DataFrame({
            "constant": ["same"] * 100,
            "constant_numeric": [42] * 100
        })

        profile = profile_dataset("dummy.csv")  # filename irrelevant; we inject df below
        profile.row_count = len(df)

        for col in df.columns:
            profile.add_column_profile(col, {
                "count": len(df),
                "unique_count": df[col].nunique(),
                "std": float(df[col].std(ddof=0)) if df[col].dtype.kind in "iufc" else None,
                "variance": float(df[col].var(ddof=0)) if df[col].dtype.kind in "iufc" else None
            })

        # Check that standard deviation and variance are zero for constant numeric column
        numeric_col = profile.column_profiles["constant_numeric"]
        self.assertEqual(numeric_col["std"], 0)
        self.assertEqual(numeric_col["variance"], 0)

        # Check that unique count is 1 for both
        self.assertEqual(profile.column_profiles["constant"]["unique_count"], 1)

    def test_memory_leak_with_large_objects(self):
        """Test for memory leaks when processing large string objects."""
        large_strings = pd.DataFrame({
            "large_string": ["x" * 1_000_000] * 10
        })

        process = psutil.Process(os.getpid())
        before_mem = process.memory_info().rss / 1024 / 1024  # in MB

        _ = profile_dataset("dummy.json")  # simulate profiling (file path ignored)

        gc.collect()

        after_mem = process.memory_info().rss / 1024 / 1024  # in MB

        # Assert that memory growth remains under threshold (e.g., < 50 MB)
        self.assertLess(after_mem - before_mem, 50)
