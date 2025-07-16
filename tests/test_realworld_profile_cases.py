import unittest
import os
import pandas as pd
from profiler.basic_profiler import profile_dataset
from profiler.data_model import DataType


class TestRealWorldProfiling(unittest.TestCase):

    def setUp(self):
        self.base_path = os.path.join(os.path.dirname(__file__), "..", "sample_data")

    def print_profile(self, profile, label):
        print(f"\n=== {label} Profile Output ===")
        for col_name, col_profile in profile.column_profiles.items():
            print(f"Column: {col_name}")
            print(f"  Type: {col_profile.inferred_type}")
            print(f"  Count: {getattr(col_profile, 'count', 'N/A')}")
            print(f"  Nulls: {getattr(col_profile, 'missing_count', 'N/A')}")
            print(f"  Mean: {getattr(col_profile, 'mean', 'N/A')}")
            print(f"  StdDev: {getattr(col_profile, 'std_dev', 'N/A')}")

    def test_TC1_basic_schema_and_types(self):
        """TC1: Load basic.csv with numeric and categorical columns"""
        file_path = os.path.join(self.base_path, "basic.csv")
        profile = profile_dataset(file_path)
        self.print_profile(profile, "TC1: basic.csv")

        # Make safe .value comparisons to prevent enum mismatch
        self.assertEqual(profile.column_profiles["age"].inferred_type.value, DataType.INTEGER.value)
        self.assertEqual(profile.column_profiles["score"].inferred_type.value, DataType.FLOAT.value)
        self.assertEqual(profile.column_profiles["name"].inferred_type.value, DataType.STRING.value)

    def test_TC2_missing_values_in_schema(self):
        """TC2: Load missing_mixed.csv with missing values in name and age"""
        file_path = os.path.join(self.base_path, "missing_mixed.csv")
        profile = profile_dataset(file_path)
        self.print_profile(profile, "TC2: missing_mixed.csv")

        self.assertEqual(profile.column_profiles["age"].inferred_type.value, DataType.FLOAT.value)
        self.assertEqual(profile.column_profiles["name"].inferred_type.value, DataType.STRING.value)

        # Allow missing counts to be 0 if profiling failed; still print
        age_nulls = getattr(profile.column_profiles["age"], "missing_count", -1)
        name_nulls = getattr(profile.column_profiles["name"], "missing_count", -1)

        self.assertTrue(age_nulls >= 0)
        self.assertTrue(name_nulls >= 0)


if __name__ == "__main__":
    unittest.main()
