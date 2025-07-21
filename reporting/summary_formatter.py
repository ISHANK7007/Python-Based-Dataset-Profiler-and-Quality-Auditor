class LazyProfiler:
    """Generate profiles lazily as needed."""
    
    def __init__(self, dataset):
        self.dataset = dataset
        self.computed_columns = {}
        
    def get_column_profile(self, column, metrics=None):
        """Get profile for a specific column, computing only if needed."""
        if column not in self.computed_columns:
            self.computed_columns[column] = {}
            
        # Check which metrics we need to compute
        metrics_to_compute = []
        if metrics:
            for metric in metrics:
                if metric not in self.computed_columns[column]:
                    metrics_to_compute.append(metric)
        
        # If we need to compute anything, do it
        if metrics_to_compute:
            new_metrics = self._compute_column_metrics(column, metrics_to_compute)
            self.computed_columns[column].update(new_metrics)
            
        # Return the requested metrics
        if metrics:
            return {metric: self.computed_columns[column].get(metric) 
                   for metric in metrics}
        else:
            return self.computed_columns[column]