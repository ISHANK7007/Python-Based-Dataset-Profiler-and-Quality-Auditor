from typing import Dict, Any

class FieldDiff:
    def __init__(self, field_name: str):
        self.field_name = field_name
        self.status = "UNCHANGED"
        self.missing_rate_change = None
        self.cardinality_change = None
        self.added_categories = set()
        self.removed_categories = set()
        self.distribution_distance = None

def calculate_distribution_distance(dist_a: Dict[Any, float], dist_b: Dict[Any, float]) -> float:
    """Compute a simple distance between two categorical distributions (e.g., L1 norm)."""
    all_keys = set(dist_a) | set(dist_b)
    return sum(abs(dist_a.get(k, 0) - dist_b.get(k, 0)) for k in all_keys)

def _calculate_change(baseline: float, current: float) -> float:
    if baseline is None or current is None:
        return None
    return current - baseline

def _diff_field_metrics(self, baseline_metrics: Dict[str, Dict], current_metrics: Dict[str, Dict]) -> Dict[str, FieldDiff]:
    """Compare field-level metrics between snapshots."""
    field_diffs = {}

    all_fields = set(baseline_metrics.keys()) | set(current_metrics.keys())

    for field in all_fields:
        field_diff = FieldDiff(field_name=field)

        if field in baseline_metrics and field not in current_metrics:
            field_diff.status = "REMOVED"
        elif field not in baseline_metrics and field in current_metrics:
            field_diff.status = "ADDED"
        else:
            field_diff.status = "MODIFIED"

            base = baseline_metrics[field]
            curr = current_metrics[field]

            field_diff.missing_rate_change = _calculate_change(
                base.get("missing_rate"), curr.get("missing_rate")
            )
            field_diff.cardinality_change = _calculate_change(
                base.get("unique_count"), curr.get("unique_count")
            )

            if "categories" in base and "categories" in curr:
                field_diff.added_categories = set(curr["categories"]) - set(base["categories"])
                field_diff.removed_categories = set(base["categories"]) - set(curr["categories"])

            if "distribution" in base and "distribution" in curr:
                field_diff.distribution_distance = calculate_distribution_distance(
                    base["distribution"], curr["distribution"]
                )

        field_diffs[field] = field_diff

    return field_diffs
