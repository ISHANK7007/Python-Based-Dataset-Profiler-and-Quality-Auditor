from typing import Optional, List

class ValidationResult:
    def __init__(self, is_valid: Optional[bool], expectation=None, message: str = ""):
        self.is_valid = is_valid
        self.expectation = expectation
        self.message = message

class ValidationReport:
    def __init__(self, results: List[ValidationResult]):
        self.results = results

    def has_failures(self):
        return any(r.is_valid is False for r in self.results)

class ComparativeExpectation:
    def validate(self, current_profile, snapshot_repository):
        raise NotImplementedError()

class NullPercentageExpectation:
    def __init__(self, field: str, max_null_pct: float):
        self.field = field
        self.max_null_pct = max_null_pct

    def validate(self, profile):
        col_profile = profile.get_column_profile(self.field)
        null_pct = col_profile.get("null_percentage", 0.0)
        is_valid = null_pct <= self.max_null_pct
        message = f"Null% for '{self.field}' = {null_pct:.2%} (allowed ≤ {self.max_null_pct:.2%})"
        return ValidationResult(is_valid, self, message)
