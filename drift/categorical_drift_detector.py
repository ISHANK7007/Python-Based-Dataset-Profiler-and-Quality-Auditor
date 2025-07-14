def detect_categorical_drift(self, column_name):
    """Detect distribution changes in categorical columns using profile metadata."""
    baseline_col = self.baseline.get_column_profile(column_name)
    current_col = self.current.get_column_profile(column_name)
    
    # Access frequent_values from our stored profile
    baseline_freqs = baseline_col.frequent_values
    current_freqs = current_col.frequent_values
    
    # Find new and missing categories
    baseline_categories = set(baseline_freqs.keys())
    current_categories = set(current_freqs.keys())
    
    new_categories = current_categories - baseline_categories
    missing_categories = baseline_categories - current_categories
    
    # Calculate frequency changes for common categories
    common_categories = baseline_categories.intersection(current_categories)
    distribution_changes = {}
    
    for category in common_categories:
        baseline_freq = baseline_freqs[category] / baseline_col.count
        current_freq = current_freqs[category] / current_col.count
        
        distribution_changes[category] = {
            'baseline_freq': baseline_freq,
            'current_freq': current_freq,
            'absolute_change': current_freq - baseline_freq,
            'percent_change': (current_freq - baseline_freq) / max(baseline_freq, 1e-9)
        }
    
    # Compute JS divergence if we have full distribution data
    divergence = None
    if len(baseline_categories) == len(current_categories) and baseline_categories == current_categories:
        # Simple implementation - in practice we'd use a proper JS divergence calculation
        divergence = sum(abs(distribution_changes[cat]['absolute_change']) for cat in common_categories) / 2
    
    return {
        'new_categories': list(new_categories),
        'missing_categories': list(missing_categories),
        'distribution_changes': distribution_changes,
        'divergence': divergence
    }