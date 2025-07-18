class SchemaEvolutionTracker:
    """Track schema changes over time at the column level."""
    
    def track_column_type_history(self, dataset_id, column_name, date_range=None):
        """Track data type changes for a column over time."""
        timeline = self.column_repo.get_column_timeline(
            dataset_id=dataset_id,
            column_name=column_name,
            metric_name='data_type',
            date_range=date_range
        )
        
        # Filter to only show changes
        type_changes = []
        last_type = None
        
        for point in timeline:
            current_type = point['value']
            if current_type != last_type:
                type_changes.append({
                    'timestamp': point['timestamp'],
                    'data_type': current_type,
                    'snapshot_id': point['snapshot_id'],
                    'metadata': point['metadata']
                })
                last_type = current_type
                
        return type_changes
        
    def generate_schema_evolution_diagram(self, dataset_id, date_range=None):
        """Generate a schema evolution diagram for a dataset."""
        # Get all columns that exist in any snapshot within the date range
        columns = self.get_all_columns(dataset_id, date_range)
        
        evolution = {}
        for column in columns:
            evolution[column] = self.track_column_type_history(dataset_id, column, date_range)
            
        # Generate diagram data
        diagram_data = self._prepare_evolution_diagram(evolution)
        return diagram_data