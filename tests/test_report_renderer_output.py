def _filter_columns(self, columns_arg):
    """Filter columns based on user input"""
    if columns_arg == 'all':
        # Use all columns from the context
        return self.context.columns
    
    # Get the specified columns
    requested_columns = columns_arg.split(',')
    
    # Filter to only include columns that exist in the dataset
    available_columns = set(self.context.columns)
    filtered_columns = [col for col in requested_columns if col in available_columns]
    
    return filtered_columns