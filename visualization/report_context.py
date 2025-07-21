class ReportContext:
    def __init__(self, baseline_profile, current_profile=None, violations=None):
        self.baseline_profile = baseline_profile
        self.current_profile = current_profile
        self.violations = violations or []

        # Determine dataset name or fallback
        self.dataset_name = getattr(baseline_profile, "name", "Dataset")

    def get_summary(self):
        # Try to return summary from profile if available
        if hasattr(self.baseline_profile, "get_summary"):
            return self.baseline_profile.get_summary()
        elif isinstance(self.baseline_profile, dict) and "summary" in self.baseline_profile:
            return self.baseline_profile["summary"]
        else:
            return {"info": "Summary not available"}
