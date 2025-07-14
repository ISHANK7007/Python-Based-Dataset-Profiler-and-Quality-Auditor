def detect_schema_drift(self):
    """Detect column additions, removals, and type changes using profile metadata."""
    # Get column sets from both profiles
    baseline_columns = set(self.baseline.get_column_names())
    current_columns = set(self.current.get_column_names())
    
    # Identify added and removed columns
    added_columns = current_columns - baseline_columns
    removed_columns = baseline_columns - current_columns
    common_columns = baseline_columns.intersection(current_columns)
    
    # Check for type changes in common columns
    type_changes = {}
    for column in common_columns:
        baseline_type = self.baseline.get_column_profile(column).inferred_type
        current_type = self.current.get_column_profile(column).inferred_type
        if baseline_type != current_type:
            type_changes[column] = {'from': baseline_type, 'to': current_type}
    
    return {
        'added_columns': list(added_columns),
        'removed_columns': list(removed_columns),
        'type_changes': type_changes
    }