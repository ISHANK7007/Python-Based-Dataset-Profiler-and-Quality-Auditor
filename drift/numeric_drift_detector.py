def detect_numeric_drift(self, column_name, threshold=0.05):
    """Detect statistical drift in numeric columns using profile metadata."""
    baseline_col = self.baseline.get_column_profile(column_name)
    current_col = self.current.get_column_profile(column_name)
    
    # Reuse existing statistics from NumericColumnStats
    drift_metrics = {
        'mean': {
            'baseline': baseline_col.mean,
            'current': current_col.mean,
            'percent_change': abs(current_col.mean - baseline_col.mean) / max(abs(baseline_col.mean), 1e-9)
        },
        'std_dev': {
            'baseline': baseline_col.std_dev,
            'current': current_col.std_dev,
            'percent_change': abs(current_col.std_dev - baseline_col.std_dev) / max(abs(baseline_col.std_dev), 1e-9)
        },
        'min': {
            'baseline': baseline_col.min_value, 
            'current': current_col.min_value
        },
        'max': {
            'baseline': baseline_col.max_value, 
            'current': current_col.max_value
        }
    }
    
    # Flag significant drifts
    is_drift_detected = (drift_metrics['mean']['percent_change'] > threshold or
                         drift_metrics['std_dev']['percent_change'] > threshold)
    
    return {
        'metrics': drift_metrics,
        'is_drift_detected': is_drift_detected
    }