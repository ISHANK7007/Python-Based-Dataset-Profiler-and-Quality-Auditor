import pandas as pd
from profiler.dataset_profile import DatasetProfile

class FakeDatasetProfile:
    def __init__(self, df, path):
        self._df = df
        self.dataset_path = path

    def get_summary(self):
        return {
            "num_rows": len(self._df),
            "num_columns": len(self._df.columns),
            "columns": list(self._df.columns),
            "sample": self._df.head(3).to_dict(orient="records")
        }

    def to_json(self):
        import json
        return json.dumps(self.get_summary(), indent=2)

def profile_dataset(path, *args, **kwargs):
    if path.endswith(".csv"):
        df = pd.read_csv(path)
    elif path.endswith(".json"):
        df = pd.read_json(path)
    else:
        raise ValueError("Unsupported file format")

    return FakeDatasetProfile(df, path)
