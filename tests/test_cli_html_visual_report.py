def _should_include_column(self, column):
    """Check if a column should be included in the report"""
    if self.filtered_columns == 'all':
        return True
    return column in self.filtered_columns

def _get_chart_type_for_violation(self, violation):
    """Determine the chart type for a violation"""
    rule_name = violation['rule']['name'].lower()
    
    if 'missing' in rule_name:
        return 'missingness'
    elif 'distribution' in rule_name or 'mean' in rule_name:
        return 'distributions'
    elif 'category' in rule_name or 'cardinality' in rule_name:
        return 'categories'
    elif 'drift' in rule_name:
        return 'drift'
    else:
        return 'violations'