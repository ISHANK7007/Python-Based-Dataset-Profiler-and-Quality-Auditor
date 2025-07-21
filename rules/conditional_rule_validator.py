import json

class MetricsRegistry:
    """Central registry for metrics with optimized computation and caching."""
    
    def __init__(self):
        self.computed_metrics = {}
        self.computation_graph = self._build_dependency_graph()
        
    def get_metric(self, dataset, column, metric_name, params=None):
        """Get a metric, computing it if necessary and caching the result."""
        key = self._create_cache_key(dataset, column, metric_name, params)
        
        if key in self.computed_metrics:
            return self.computed_metrics[key]
        
        if self._can_derive_from_cache(key, metric_name):
            value = self._derive_from_cache(key, metric_name)
            self.computed_metrics[key] = value
            return value
        
        value = self._compute_metric(dataset, column, metric_name, params)
        self.computed_metrics[key] = value
        return value
    
    def _create_cache_key(self, dataset, column, metric_name, params):
        param_str = json.dumps(params, sort_keys=True) if params else ""
        return f"{dataset.id}:{column}:{metric_name}:{param_str}"
    
    def _can_derive_from_cache(self, key, metric_name):
        dependencies = self.computation_graph.get(metric_name, [])
        if not dependencies:
            return False

        parts = key.split(":")
        dataset_id, column = parts[0], parts[1]

        for dep_metric in dependencies:
            dep_key_prefix = f"{dataset_id}:{column}:{dep_metric}:"
            if not any(k.startswith(dep_key_prefix) for k in self.computed_metrics):
                return False
        return True
    
    def _derive_from_cache(self, key, metric_name):
        parts = key.split(":")
        dataset_id, column = parts[0], parts[1]

        def get_cached_value(metric):
            key_prefix = f"{dataset_id}:{column}:{metric}:"
            return next((v for k, v in self.computed_metrics.items() if k.startswith(key_prefix)), None)

        if metric_name == "mean":
            sum_val = get_cached_value("sum")
            count_val = get_cached_value("count")
            return sum_val / count_val if sum_val is not None and count_val else None
        
        elif metric_name == "null_percent":
            null_count = get_cached_value("null_count")
            count = get_cached_value("count")
            return (null_count / count * 100) if null_count is not None and count else None
        
        elif metric_name == "variance":
            sum_squared = get_cached_value("sum_squared")
            sum_val = get_cached_value("sum")
            count_val = get_cached_value("count")
            if all(v is not None for v in [sum_squared, sum_val, count_val]) and count_val > 0:
                mean = sum_val / count_val
                return (sum_squared / count_val) - (mean ** 2)
            return None

        raise ValueError(f"Cannot derive metric: {metric_name}")

    def _compute_metric(self, dataset, column, metric_name, params):
        # Placeholder for actual logic — plug into profiling system here
        raise NotImplementedError(f"Metric computation for '{metric_name}' not implemented.")

    def _build_dependency_graph(self):
        return {
            "mean": ["sum", "count"],
            "variance": ["sum_squared", "sum", "count"],
            "null_percent": ["null_count", "count"],
        }
