class ReportRenderer:
    def __init__(self, report_context, output_format='html', config=None):
        # Existing initialization...
        
        # Process chart selection
        self.enabled_charts = self._process_chart_selection(config.get('charts', 'all'))
    
    def _process_chart_selection(self, charts_arg):
        """Process the charts argument to determine which types to enable"""
        all_chart_types = {
            'summary': True,      # Summary/overview charts
            'distributions': True, # Distribution charts for numeric columns
            'missingness': True,   # Missing value visualizations
            'categories': True,    # Categorical charts
            'violations': True,    # Violation-specific charts
            'drift': True          # Drift comparison charts
        }
        
        # If 'all', enable everything
        if charts_arg == 'all':
            return all_chart_types
        
        # If 'none', disable everything (will still show text summaries)
        if charts_arg == 'none':
            return {k: False for k in all_chart_types}
        
        # Parse comma-separated list
        enabled_types = charts_arg.split(',')
        
        # Create a dict with only specified chart types enabled
        result = {k: (k in enabled_types) for k in all_chart_types}
        
        return result
    
    def _should_render_chart(self, chart_type, column=None, violation=None):
        """Check if a specific chart should be rendered based on config"""
        # First check if the chart category is enabled
        if not self.enabled_charts.get(chart_type, False):
            return False
            
        # Additional filters could be applied here
        # For example, column-specific filtering
        if column and self.config.get('column_filter'):
            if column not in self.config.get('column_filter').split(','):
                return False
        
        # Severity-based filtering for violation charts
        if violation and self.config.get('min_severity'):
            severity_rank = self._get_severity_rank(violation['rule']['severity'])
            min_rank = self._get_severity_rank(self.config.get('min_severity'))
            if severity_rank < min_rank:
                return False
        
        return True
    
    def _generate_all_charts(self):
        """Generate all charts needed for the report"""
        charts = {}
        
        # Only generate charts that are enabled
        
        # Summary charts
        if self._should_render_chart('summary'):
            charts['summary-violations'] = self._generate_violations_summary_chart()
            
            if self.context.is_drift_report and self._should_render_chart('drift'):
                charts['summary-drift'] = self._generate_drift_summary_chart()
        
        # Column-specific charts
        for column in self.context.columns:
            # Distribution charts for numeric columns
            if (self._should_render_chart('distributions', column) and 
                self._is_numeric_column(column)):
                chart_id = f"distribution-{self._sanitize_id(column)}"
                charts[chart_id] = self._generate_distribution_chart(column)
            
            # Missing value charts
            if (self._should_render_chart('missingness', column) and 
                self._has_missing_values(column)):
                chart_id = f"missing-{self._sanitize_id(column)}"
                charts[chart_id] = self._generate_missing_values_chart(column)
            
            # Category charts for categorical columns
            if (self._should_render_chart('categories', column) and 
                self._is_categorical(column)):
                chart_id = f"categories-{self._sanitize_id(column)}"
                charts[chart_id] = self._generate_category_chart(column)
        
        # Violation-specific charts
        if self._should_render_chart('violations'):
            for violation in self.context.violations:
                chart_id = self._get_chart_id(violation)
                charts[chart_id] = self._generate_chart_for_violation(violation)
        
        return charts