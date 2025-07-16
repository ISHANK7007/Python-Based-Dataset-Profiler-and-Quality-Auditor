def get_distribution_change_metadata(drift_report, column_name):
    """Extract relevant distribution change metrics for explanations"""
    column_drift = drift_report.get_column_drift(column_name)
    return {
        'column': column_name,
        'ks_value': column_drift.distribution_distance,
        'old_mean': column_drift.baseline_stats.mean,
        'new_mean': column_drift.current_stats.mean,
        'std_change_pct': (column_drift.current_stats.std - column_drift.baseline_stats.std) / 
                           column_drift.baseline_stats.std * 100 if column_drift.baseline_stats.std > 0 else 0,
        'is_significant': column_drift.is_significant
    }