def to_excel(self, filename):
    """Export drift report to Excel with multiple worksheets."""
    import pandas as pd
    
    # Create a Pandas Excel writer
    writer = pd.ExcelWriter(filename, engine='xlsxwriter')
    
    # Summary sheet
    summary_df = pd.DataFrame({
        'Metric': ['Total Columns', 'Columns With Drift', 
                  'Major Drifts', 'Moderate Drifts', 'Minor Drifts'],
        'Value': [
            self.summary['total_columns_analyzed'],
            self.summary['total_columns_with_drift'],
            self.summary['drift_by_severity']['major'],
            self.summary['drift_by_severity']['moderate'],
            self.summary['drift_by_severity']['minor']
        ]
    })
    summary_df.to_excel(writer, sheet_name='Summary', index=False)
    
    # Additional sheets for each drift type
    # ...
    
    writer.save()