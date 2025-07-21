import time
import math
import sys
from collections import defaultdict
from typing import Any, Dict, List

class MetricCacheManager:
    """Manage caching of metrics with intelligent retention."""

    def __init__(self, max_cache_size_mb: int = 1000):
        self.cache: Dict[str, Any] = {}
        self.cache_size: int = 0
        self.max_cache_size: int = max_cache_size_mb * 1024 * 1024  # Convert MB to bytes
        self.access_history: Dict[str, Dict[str, Any]] = {}

    def add_to_cache(self, key: str, value: Any) -> None:
        """Add a metric to cache with size tracking."""
        value_size = self._estimate_size(value)

        if self.cache_size + value_size > self.max_cache_size:
            self._evict_cache_entries(required_size=value_size)

        self.cache[key] = value
        self.cache_size += value_size
        self.access_history[key] = {"last_access": time.time(), "access_count": 1}

    def get_from_cache(self, key: str) -> Any:
        """Get a metric from cache, updating access history."""
        if key in self.cache:
            self.access_history[key]["last_access"] = time.time()
            self.access_history[key]["access_count"] += 1
            return self.cache[key]
        return None

    def _evict_cache_entries(self, required_size: int) -> None:
        """Intelligently evict cache entries to make room."""
        if not self.cache:
            return

        now = time.time()
        scores = {}

        for key, value in self.cache.items():
            recency = now - self.access_history[key]["last_access"]
            frequency = self.access_history[key]["access_count"]
            size = self._estimate_size(value)
            scores[key] = recency / (frequency * math.sqrt(size) + 1e-6)  # Avoid div/0

        keys_to_evict = sorted(scores, key=scores.get, reverse=True)

        space_freed = 0
        for key in keys_to_evict:
            value_size = self._estimate_size(self.cache[key])
            del self.cache[key]
            del self.access_history[key]
            self.cache_size -= value_size
            space_freed += value_size

            if space_freed >= required_size:
                break

    def warm_cache_for_expectations(self, expectations: List[Any], dataset: Any) -> None:
        """Pre-compute and cache metrics required by a set of expectations."""
        required_metrics = self._identify_required_metrics(expectations)

        for column, metrics in required_metrics.items():
            for metric in metrics:
                key = f"{dataset.id}:{column}:{metric}"
                if key not in self.cache:
                    value = self._compute_metric(dataset, column, metric)
                    self.add_to_cache(key, value)

    def _identify_required_metrics(self, expectations: List[Any]) -> Dict[str, List[str]]:
        """Scan expectations to extract metric requirements."""
        metrics = defaultdict(set)
        for exp in expectations:
            if hasattr(exp, "column_name") and hasattr(exp, "metric"):
                metrics[exp.column_name].add(exp.metric)
        return {col: list(m) for col, m in metrics.items()}

    def _estimate_size(self, obj: Any) -> int:
        """Roughly estimate the memory size of a metric object."""
        try:
            return sys.getsizeof(obj)
        except Exception:
            return 512  # Fallback default size

    def _compute_metric(self, dataset: Any, column: str, metric: str) -> Any:
        """Simulate metric computation. Replace with real logic."""
        stats = dataset.get_column_stats(column)
        return stats.get(metric, None)
