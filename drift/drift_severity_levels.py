def detect_quality_drift(self, column_name):
    """Detect changes in data quality metrics using profile metadata."""
    baseline_col = self.baseline.get_column_profile(column_name)
    current_col = self.current.get_column_profile(column_name)
    
    # Compare missing value rates
    baseline_missing_rate = baseline_col.missing_count / baseline_col.count
    current_missing_rate = current_col.missing_count / current_col.count
    
    # Compare uniqueness
    baseline_uniqueness = baseline_col.unique_count / baseline_col.count
    current_uniqueness = current_col.unique_count / current_col.count
    
    return {
        'missing_values': {
            'baseline_rate': baseline_missing_rate,
            'current_rate': current_missing_rate,
            'absolute_change': current_missing_rate - baseline_missing_rate
        },
        'uniqueness': {
            'baseline_rate': baseline_uniqueness,
            'current_rate': current_uniqueness,
            'absolute_change': current_uniqueness - baseline_uniqueness
        }
    }