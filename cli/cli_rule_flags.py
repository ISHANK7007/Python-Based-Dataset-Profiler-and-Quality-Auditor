from typing import Optional, Any

# --- Placeholder base and result classes ---
class GroupedExpectation:
    def __init__(self, **kwargs):
        pass

class GroupSingleResult:
    def __init__(self, group_key: Any, is_valid: Optional[bool],
                 actual_value: Optional[float] = None,
                 expected_min: Optional[float] = None,
                 expected_max: Optional[float] = None,
                 message: str = ""):
        self.group_key = group_key
        self.is_valid = is_valid
        self.actual_value = actual_value
        self.expected_min = expected_min
        self.expected_max = expected_max
        self.message = message

# --- Final Implementation ---
class GroupedMetricRangeExpectation(GroupedExpectation):
    """Validate that a column metric falls within a range for each group."""

    def __init__(self, column: str, metric: str,
                 min_value: Optional[float] = None,
                 max_value: Optional[float] = None, **kwargs):
        super().__init__(**kwargs)
        self.column = column
        self.metric = metric  # e.g., "mean", "null_percent"
        self.min_value = min_value
        self.max_value = max_value

    def _validate_group(self, group_key: Any, group_profile) -> GroupSingleResult:
        column_stats = group_profile.get_column_stats(self.column)
        metric_value = column_stats.get(self.metric)

        if metric_value is None:
            return GroupSingleResult(
                group_key=group_key,
                is_valid=None,
                message=f"Metric '{self.metric}' not available for group '{group_key}'"
            )

        min_valid = self.min_value is None or metric_value >= self.min_value
        max_valid = self.max_value is None or metric_value <= self.max_value
        is_valid = min_valid and max_valid

        return GroupSingleResult(
            group_key=group_key,
            is_valid=is_valid,
            actual_value=metric_value,
            expected_min=self.min_value,
            expected_max=self.max_value,
            message=self._generate_group_message(group_key, is_valid, metric_value)
        )

    def _generate_group_message(self, group_key: Any, is_valid: bool, value: float) -> str:
        if is_valid:
            return f"Group '{group_key}': {self.column} {self.metric} = {value} is within expected range"

        if self.min_value is not None and value < self.min_value:
            return f"Group '{group_key}': {self.column} {self.metric} = {value} is below minimum {self.min_value}"

        if self.max_value is not None and value > self.max_value:
            return f"Group '{group_key}': {self.column} {self.metric} = {value} exceeds maximum {self.max_value}"

        return f"Group '{group_key}': {self.column} {self.metric} = {value} is out of expected range"
