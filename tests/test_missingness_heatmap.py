def _apply_chart_preset(self, preset):
    """Apply chart preset configurations"""
    presets = {
        'minimal': {
            'charts': 'summary,violations',
            'chart_detail_level': 'low'
        },
        'basic': {
            'charts': 'summary,violations,missingness',
            'chart_detail_level': 'medium'
        },
        'standard': {
            'charts': 'summary,violations,missingness,distributions',
            'chart_detail_level': 'medium'
        },
        'comprehensive': {
            'charts': 'all',
            'chart_detail_level': 'high'
        }
    }
    
    # Update config with preset values
    if preset in presets:
        for key, value in presets[preset].items():
            if key not in self.config:  # Don't override explicit settings
                self.config[key] = value