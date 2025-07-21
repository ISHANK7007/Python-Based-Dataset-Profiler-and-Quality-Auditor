from typing import Optional, Dict, Any
import random

# Placeholder base and result classes
class GroupedExpectation:
    def __init__(self, group_by: str = None, filter_condition: Optional[str] = None, **kwargs):
        self.group_by = group_by
        self.filter_condition = filter_condition

class GroupSingleResult:
    def __init__(self, group_key, is_valid, message, actual_value=None, expected_min=None, expected_max=None):
        self.group_key = group_key
        self.is_valid = is_valid
        self.message = message
        self.actual_value = actual_value
        self.expected_min = expected_min
        self.expected_max = expected_max

class GroupValidationResult:
    def __init__(self, is_valid, expectation, group_results):
        self.is_valid = is_valid
        self.expectation = expectation
        self.group_results = group_results

    def get_failed_groups(self):
        return [r for r in self.group_results if r.is_valid is False]

# Fully implemented expectation
class GroupedMetricRangeExpectation(GroupedExpectation):
    def __init__(self, column: str, metric: str, min_value=None, max_value=None,
                 min_group_size: int = 0, group_sample: Optional[int] = None, **kwargs):
        super().__init__(**kwargs)
        self.column = column
        self.metric = metric
        self.min_value = min_value
        self.max_value = max_value
        self.min_group_size = min_group_size
        self.group_sample = group_sample

    def validate(self, profile) -> GroupValidationResult:
        grouped_metrics = profile.get_grouped_metrics(
            group_by=self.group_by,
            filter_condition=self.filter_condition
        )

        if self.min_group_size > 0:
            grouped_metrics = {
                k: v for k, v in grouped_metrics.items()
                if v.row_count >= self.min_group_size
            }

        if self.group_sample and len(grouped_metrics) > self.group_sample:
            grouped_metrics = self._sample_groups(grouped_metrics, self.group_sample)

        group_results = []
        for group_key, group_profile in grouped_metrics.items():
            group_result = self._validate_group(group_key, group_profile)
            group_results.append(group_result)

        overall_valid = all(gr.is_valid is not False for gr in group_results)
        return GroupValidationResult(is_valid=overall_valid, expectation=self, group_results=group_results)

    def _validate_group(self, group_key, group_profile) -> GroupSingleResult:
        stats = group_profile.get_column_stats(self.column)
        value = stats.get(self.metric)

        if value is None:
            return GroupSingleResult(
                group_key=group_key,
                is_valid=None,
                message=f"Metric '{self.metric}' missing for group '{group_key}'"
            )

        min_ok = self.min_value is None or value >= self.min_value
        max_ok = self.max_value is None or value <= self.max_value
        is_valid = min_ok and max_ok

        return GroupSingleResult(
            group_key=group_key,
            is_valid=is_valid,
            actual_value=value,
            expected_min=self.min_value,
            expected_max=self.max_value,
            message=self._generate_group_message(group_key, value, is_valid)
        )

    def _generate_group_message(self, group_key, value, is_valid):
        if is_valid:
            return f"Group '{group_key}': {self.column} {self.metric} = {value} within range"
        if self.min_value is not None and value < self.min_value:
            return f"Group '{group_key}': {self.column} {self.metric} = {value} < min {self.min_value}"
        if self.max_value is not None and value > self.max_value:
            return f"Group '{group_key}': {self.column} {self.metric} = {value} > max {self.max_value}"
        return f"Group '{group_key}': {self.column} {self.metric} = {value} out of range"

    def _sample_groups(self, groups: Dict[Any, Any], sample_size: int) -> Dict[Any, Any]:
        sampled_keys = random.sample(list(groups.keys()), sample_size)
        return {k: groups[k] for k in sampled_keys}
