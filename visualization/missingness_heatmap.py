class ChartGenerator:
    def __init__(self, data_extractor):
        self.extractor = data_extractor
        
    def generate_column_visualization(self, column_name):
        """Generate appropriate visualization based on column type and available stats"""
        baseline_stats, current_stats = self.extractor.get_column_statistics(column_name)
        column_type = baseline_stats['basic_stats']['type']
        
        if current_stats:  # Drift comparison mode
            return self._generate_comparison_chart(column_name, column_type, baseline_stats, current_stats)
        else:  # Single profile mode
            return self._generate_profile_chart(column_name, column_type, baseline_stats)
    
    def _generate_comparison_chart(self, column_name, column_type, baseline_stats, current_stats):
        if column_type == 'numeric':
            return self._generate_distribution_comparison(column_name, baseline_stats, current_stats)
        elif column_type == 'categorical':
            return self._generate_category_drift_chart(column_name, baseline_stats, current_stats)
        else:  # date, text, etc.
            return self._generate_stats_comparison(column_name, baseline_stats, current_stats)