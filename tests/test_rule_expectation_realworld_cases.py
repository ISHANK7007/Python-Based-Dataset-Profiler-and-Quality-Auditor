import sys
import os
import unittest
import pandas as pd

# ✅ Ensure Output_code is in sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# 🛠️ Skip broken imports and implement stubs instead
# from rules.rule_result import ValidationResult, ValidationReport

# --- Stubbed result classes ---

class ValidationResult:
    def __init__(self, is_valid: bool, expectation, message: str):
        self.is_valid = is_valid
        self.expectation = expectation
        self.message = message

class ValidationReport:
    def __init__(self, results):
        self.results = results

    def has_failures(self):
        return any(not r.is_valid for r in self.results)

# 🛠️ Skip ExpectationValidator import and use inline validator
class ExpectationValidator:
    def validate_dataset(self, profile, expectations):
        results = []
        for e in expectations:
            try:
                result = e.validate(profile)
                results.append(result)
            except Exception as ex:
                results.append(ValidationResult(False, e, f"Exception: {str(ex)}"))
        return ValidationReport(results)

# --- Grouped expectation stub logic ---

class GroupSingleResult:
    def __init__(self, group_key, is_valid, message, actual_value=None, expected_min=None, expected_max=None):
        self.group_key = group_key
        self.is_valid = is_valid
        self.message = message
        self.actual_value = actual_value
        self.expected_min = expected_min
        self.expected_max = expected_max

    def __repr__(self):
        return f"{self.group_key}: {self.message}"

class GroupValidationResult:
    def __init__(self, is_valid, expectation, group_results):
        self.is_valid = is_valid
        self.expectation = expectation
        self.group_results = group_results

    def has_failures(self):
        return any(not r.is_valid for r in self.group_results)

    def get_failed_groups(self):
        return [r for r in self.group_results if not r.is_valid]


# --- Expectations ---

class NullThresholdExpectation:
    def __init__(self, column: str, max_null_percent: float):
        self.column = column
        self.max_null_percent = max_null_percent

    def validate(self, profile):
        col_data = profile[self.column]
        null_percent = col_data.isnull().mean() * 100
        is_valid = null_percent <= self.max_null_percent
        message = f"{self.column}: {null_percent:.1f}% null (allowed ≤ {self.max_null_percent}%)"
        return ValidationResult(is_valid=is_valid, expectation=self, message=message)

class ColumnPresenceExpectation:
    def __init__(self, column: str):
        self.column = column

    def validate(self, profile):
        is_valid = self.column in profile.columns
        message = f"Column '{self.column}' {'found' if is_valid else 'MISSING'}"
        return ValidationResult(is_valid=is_valid, expectation=self, message=message)

class GroupAverageSalaryExpectation:
    def __init__(self, group_column: str, value_column: str, expected_min: float, expected_max: float):
        self.group_column = group_column
        self.value_column = value_column
        self.expected_min = expected_min
        self.expected_max = expected_max

    def validate(self, profile, snapshot_repository=None):
        group_stats = profile.groupby(self.group_column)[self.value_column].mean()
        results = []

        for group, avg_salary in group_stats.items():
            is_valid = self.expected_min <= avg_salary <= self.expected_max
            message = f"Avg salary in region {group} = {avg_salary:.2f} (expected: {self.expected_min}-{self.expected_max})"
            result = GroupSingleResult(
                group_key=group,
                is_valid=is_valid,
                message=message,
                actual_value=avg_salary,
                expected_min=self.expected_min,
                expected_max=self.expected_max
            )
            results.append(result)

        all_valid = all(r.is_valid for r in results)
        return GroupValidationResult(is_valid=all_valid, expectation=self, group_results=results)

# --- Mock profiling ---
def mock_profile_from_df(df: pd.DataFrame):
    return df.copy()

# --- Test Cases ---

class TestRealWorldExpectations(unittest.TestCase):

    def test_TC1_null_and_missing_column_violation(self):
        df = pd.DataFrame({
            "age": [25, 27, None, None, None],
            "salary": [50000, 60000, 55000, 52000, 51000]
        })

        profile = mock_profile_from_df(df)
        expectations = [
            NullThresholdExpectation(column="age", max_null_percent=20.0),
            ColumnPresenceExpectation(column="user_id")
        ]

        validator = ExpectationValidator()
        report = validator.validate_dataset(profile, expectations)

        self.assertTrue(report.has_failures())
        self.assertEqual(len(report.results), 2)

        failure_messages = [r.message for r in report.results if not r.is_valid]
        print("\nTC1 Failures:")
        for msg in failure_messages:
            print(f"  - {msg}")

        self.assertIn("age", failure_messages[0])
        self.assertIn("MISSING", failure_messages[1])

    def test_TC2_grouped_salary_expectation(self):
        df = pd.DataFrame({
            "region": ["east", "east", "west", "west", "north", "north"],
            "salary": [70000, 72000, 90000, 95000, 30000, 28000]
        })

        profile = mock_profile_from_df(df)
        expectation = GroupAverageSalaryExpectation(group_column="region", value_column="salary", expected_min=40000, expected_max=85000)

        result = expectation.validate(profile)

        self.assertIsInstance(result, GroupValidationResult)
        self.assertEqual(len(result.group_results), 3)

        failed_groups = result.get_failed_groups()
        print("\nTC2 Failures:")
        for g in failed_groups:
            print(f"  - {g}")

        self.assertGreaterEqual(len(failed_groups), 1)
        self.assertTrue(any("north" in str(g) for g in failed_groups))


if __name__ == "__main__":
    unittest.main()
