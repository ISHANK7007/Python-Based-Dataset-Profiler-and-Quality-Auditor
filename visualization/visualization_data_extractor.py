class VisualizationDataExtractor:
    def __init__(self, baseline_profile, current_profile=None):
        self.baseline = baseline_profile
        self.current = current_profile

    def get_visualizable_columns(self):
        """Return a list of columns common to both profiles (or just baseline if current not available)."""
        if self.current:
            return list(set(self.baseline.keys()) & set(self.current.keys()))
        return list(self.baseline.keys())

    def get_summary_statistics(self):
        """Return simple drift statistics summary for report header."""
        total = len(self.baseline)
        drifted = 0
        if self.current:
            for col in self.get_visualizable_columns():
                if self.baseline[col] != self.current.get(col):
                    drifted += 1
        return {
            "total_columns": total,
            "drift_detected": drifted,
            "drift_ratio": f"{drifted}/{total}"
        }
