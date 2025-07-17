class StatisticsCache:
    def __init__(self):
        # Structure: {dataset_id: {column_name: {stat_name: value}}}
        self.stats = {}

    def get(self, dataset_id, column, stat_name, default=None):
        return self.stats.get(dataset_id, {}).get(column, {}).get(stat_name, default)

    def set(self, dataset_id, column, stat_name, value):
        self.stats.setdefault(dataset_id, {}).setdefault(column, {})[stat_name] = value


# === Rule Functions That Use the Cache ===

def missing_rate(stats_cache, dataset_id, column):
    value = stats_cache.get(dataset_id, column, "missing_rate")
    if value is None:
        # Return default or simulate computation fallback
        return 0.0
    return value

def unique_count(stats_cache, dataset_id, column):
    value = stats_cache.get(dataset_id, column, "unique_count")
    if value is None:
        return 0
    return value
