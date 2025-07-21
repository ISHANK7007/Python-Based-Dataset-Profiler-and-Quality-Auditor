def _std(self, context, field):
    # Safely get standard deviation from the context
    return context.get_statistic('std', field)
    
def _mode(self, context, field):
    # Safely get mode from the context
    return context.get_statistic('mode', field)
    
# Other statistical function implementations...