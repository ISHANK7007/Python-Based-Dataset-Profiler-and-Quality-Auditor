def generate_drift_report(self):
    """Generate a comprehensive drift report reusing profile metadata."""
    # Detect schema drift
    schema_drift = self.detect_schema_drift()
    self.drift_report.schema_drift = schema_drift
    
    # For common columns, detect statistical and quality drift
    common_columns = set(self.baseline.get_column_names()).intersection(
        set(self.current.get_column_names())
    )
    
    for column in common_columns:
        column_type = self.baseline.get_column_profile(column).inferred_type
        
        # Add quality drift metrics for all columns
        self.drift_report.add_column_quality_drift(
            column, self.detect_quality_drift(column)
        )
        
        # Add distribution drift metrics based on column type
        if column_type in ['integer', 'float', 'numeric']:
            self.drift_report.add_column_distribution_drift(
                column, 'numeric', self.detect_numeric_drift(column)
            )
        elif column_type in ['string', 'boolean', 'categorical']:
            self.drift_report.add_column_distribution_drift(
                column, 'categorical', self.detect_categorical_drift(column)
            )
    
    return self.drift_report