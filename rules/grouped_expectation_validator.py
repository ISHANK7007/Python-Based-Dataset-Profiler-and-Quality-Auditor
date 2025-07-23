from typing import Any

# Assumed base class and result structure
class ComparativeExpectation:
    def __init__(self, column_name: str, **kwargs):
        self.column_name = column_name

class ValidationResult:
    def __init__(self, is_valid: bool, expectation: Any, actual_value: float,
                 expected_value: float, message: str):
        self.is_valid = is_valid
        self.expectation = expectation
        self.actual_value = actual_value
        self.expected_value = expected_value
        self.message = message

class NoNullIncreaseExpectation(ComparativeExpectation):
    """Ensure null percentage hasn't increased beyond tolerance for a column."""
    
    def __init__(self, column_name: str, tolerance: float = 0.0, **kwargs):
        super().__init__(column_name=column_name, **kwargs)
        self.tolerance = tolerance

    def _compare_profiles(self, current_profile, baseline_profile) -> ValidationResult:
        # Extract column-level null percentages
        current_stats = current_profile.get_column_stats(self.column_name)
        baseline_stats = baseline_profile.get_column_stats(self.column_name)

        current_null_pct = current_stats.get("null_percent", 0.0)
        baseline_null_pct = baseline_stats.get("null_percent", 0.0)

        increase = current_null_pct - baseline_null_pct
        is_valid = increase <= self.tolerance

        return ValidationResult(
            is_valid=is_valid,
            expectation=self,
            actual_value=increase,
            expected_value=self.tolerance,
            message=self._generate_message(is_valid, current_null_pct, baseline_null_pct, increase)
        )

    def _generate_message(self, is_valid: bool, current: float, baseline: float, increase: float) -> str:
        if is_valid:
            return (f"Column '{self.column_name}' null percentage change of {increase:.2f}% "
                    f"is within tolerance ({self.tolerance:.2f}%).")
        else:
            return (f"Column '{self.column_name}' null percentage increased by {increase:.2f}% "
                    f"(from {baseline:.2f}% to {current:.2f}%), exceeding tolerance of {self.tolerance:.2f}%.")
