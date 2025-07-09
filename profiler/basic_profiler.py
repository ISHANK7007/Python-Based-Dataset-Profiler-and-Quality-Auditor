import os
from profiler.dataset_profile import DatasetProfile
from profiler.data_model import ColumnProfile, DataType
from profiler.column_type_inferer import detect_column_type
from profiler.numeric_profile_optimized import profile_numeric_column_optimized
from profiler.profile_variants import CsvProfile, JsonProfile


def load_data(dataset_path: str):
    """Load dataset using appropriate profile subclass based on file extension."""
    ext = os.path.splitext(dataset_path)[1].lower()
    if ext == ".csv":
        profile = CsvProfile(dataset_path)
        return profile.load_data()
    elif ext == ".json":
        profile = JsonProfile(dataset_path)
        return profile.load_data()
    else:
        raise ValueError(f"Unsupported file type: {ext}")


def profile_dataset(dataset_path: str) -> DatasetProfile:
    """Profiles a dataset from the given path and returns a DatasetProfile."""
    # Create base profile
    profile = DatasetProfile(dataset_path)

    # Load data
    df = load_data(dataset_path)
    if df is None:
        raise ValueError("Failed to load dataset.")

    # Basic dataset info
    profile.row_count = len(df)
    profile.metadata["column_count"] = len(df.columns)

    # Profile each column
    for column in df.columns:
        # Detect column type
        dtype = detect_column_type(df[column])

        # Create column profile
        col_profile = ColumnProfile(name=column, inferred_type=dtype)

        # If numeric, add numeric stats
        if dtype in {DataType.NUMERIC, DataType.INTEGER, DataType.FLOAT}:
            numeric_stats = profile_numeric_column_optimized(df, column, profile.row_count)

            col_profile.count = numeric_stats.get("count")
            col_profile.missing_count = df[column].isna().sum()
            col_profile.min_value = numeric_stats.get("min")
            col_profile.max_value = numeric_stats.get("max")
            col_profile.mean = numeric_stats.get("mean")
            col_profile.median = numeric_stats.get("median")
            col_profile.std_dev = numeric_stats.get("std")

        # Add column profile
        profile.add_column_profile(column, col_profile)

    return profile
