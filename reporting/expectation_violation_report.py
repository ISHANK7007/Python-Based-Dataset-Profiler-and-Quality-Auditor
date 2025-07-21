from typing import Any

# Placeholder base classes for context
class ColumnExpectation:
    def __init__(self, column_name: str):
        self.column_name = column_name

class ValidationResult:
    def __init__(self, is_valid: bool, message: str, actual_value: Any = None, expected_value: Any = None):
        self.is_valid = is_valid
        self.message = message
        self.actual_value = actual_value
        self.expected_value = expected_value

class NullPercentageExpectation(ColumnExpectation):
    """Validate that null percentage of a column is within the expected threshold."""

    def __init__(self, column_name: str, threshold: float, operator: str = "<"):
        super().__init__(column_name)
        self.threshold = threshold
        self.operator = operator

    def validate(self, dataset_summaries) -> ValidationResult:
        column_stats = dataset_summaries.get_column_stats(self.column_name)
        actual_null_percent = column_stats.get("null_percent")

        if actual_null_percent is None:
            return ValidationResult(
                is_valid=False,
                message=f"Null percentage for column '{self.column_name}' not found.",
                actual_value=None,
                expected_value=self.threshold
            )

        is_valid = self._compare(actual_null_percent, self.threshold, self.operator)

        return ValidationResult(
            is_valid=is_valid,
            message=self._generate_message(is_valid, actual_null_percent),
            actual_value=actual_null_percent,
            expected_value=self.threshold
        )

    def _compare(self, actual: float, expected: float, operator: str) -> bool:
        if operator == "<":
            return actual < expected
        elif operator == "<=":
            return actual <= expected
        elif operator == ">":
            return actual > expected
        elif operator == ">=":
            return actual >= expected
        elif operator == "==":
            return actual == expected
        else:
            raise ValueError(f"Unsupported comparison operator: '{operator}'")

    def _generate_message(self, is_valid: bool, actual: float) -> str:
        if is_valid:
            return (f"✅ Null percentage for column '{self.column_name}' is {actual:.2f}%, "
                    f"which meets expectation ({self.operator} {self.threshold}%).")
        else:
            return (f"❌ Null percentage for column '{self.column_name}' is {actual:.2f}%, "
                    f"which violates expectation ({self.operator} {self.threshold}%).")
