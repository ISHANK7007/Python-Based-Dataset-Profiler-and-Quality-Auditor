class VisualizationDataExtractor:
    def __init__(self, baseline_profile, current_profile=None):
        self.baseline = baseline_profile
        self.current = current_profile
        
    def get_column_statistics(self, column_name):
        """Extract relevant statistics for a specific column from profile(s)"""
        baseline_stats = self._extract_stats(self.baseline, column_name)
        current_stats = None
        if self.current:
            current_stats = self._extract_stats(self.current, column_name)
        return baseline_stats, current_stats
    
    def _extract_stats(self, profile, column_name):
        # Access cached statistics from profile JSON structure
        # Return formatted for visualization consumption
        return {
            'basic_stats': self._get_basic_stats(profile, column_name),
            'distribution': self._get_distribution(profile, column_name),
            'missing_data': self._get_missing_data(profile, column_name),
            'unique_values': self._get_unique_values(profile, column_name)
        }