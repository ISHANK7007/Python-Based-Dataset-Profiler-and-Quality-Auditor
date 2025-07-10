from profiler.dataset_profile import DatasetProfile
from drift.drift_report_generator import DriftReport

class ProfileComparer:
    def __init__(self, baseline_profile: DatasetProfile, current_profile: DatasetProfile):
        """
        Initialize with two DatasetProfile instances to compare.
        """
        self.baseline = baseline_profile
        self.current = current_profile
        self.drift_report = DriftReport()

    def compare(self):
        """
        Run full drift detection between the two profiles and return a report.
        """
        schema_drift = self.drift_report.detect_schema_drift(self.baseline, self.current)
        numeric_drift = self.drift_report.detect_numeric_drift(self.baseline, self.current)
        categorical_drift = self.drift_report.detect_categorical_drift(self.baseline, self.current)

        return {
            "schema_drift": schema_drift,
            "numeric_drift": numeric_drift,
            "categorical_drift": categorical_drift,
        }
