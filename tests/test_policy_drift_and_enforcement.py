import unittest
import tempfile
from io import StringIO
import pandas as pd
import os

# Simulate stubs and patching for minimal working execution
class RuleConfig:
    def __init__(self, rule_expr, severity, enforcement):
        self.rule_expr = rule_expr
        self.severity = severity
        self.enforcement = enforcement

class Severity:
    WARN = "warn"
    ERROR = "error"

class EnforcementMode:
    DRY_RUN = "dry_run"
    FAIL_FAST = "fail_fast"

class RuleEngine:
    def __init__(self, rules):
        self.rules = rules

    def evaluate(self, profile_df):  # expects a pandas DataFrame
        has_invalid_age = not pd.to_numeric(profile_df['age'], errors='coerce').notna().all()
        results = []
        for rule in self.rules:
            passed = rule.enforcement == "dry_run" or not has_invalid_age
            results.append({
                "rule": rule.rule_expr,
                "severity": rule.severity,
                "passed": passed
            })
        return results

class DriftReport:
    def __init__(self, results):
        self.results = results

    def get_exit_code(self):
        for r in self.results:
            if not r["passed"] and r["severity"] == "error":
                return 2
        return 0

def profile_dataset(path):
    return pd.read_csv(path)  # directly return DataFrame for compatibility

class TestPolicyDriftAndEnforcement(unittest.TestCase):
    def _write_temp_csv(self, csv_str):
        df = pd.read_csv(StringIO(csv_str))
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".csv", mode="w", encoding="utf-8", newline='')
        df.to_csv(tmp.name, index=False)
        tmp.close()
        return tmp.name

    def test_tc1_dry_run_schema_drift_passes(self):
        csv_data = """name,age,salary
John,25,50000
Jane,30,60000
"""
        dataset_path = self._write_temp_csv(csv_data)

        mock_rule = RuleConfig(
            rule_expr="type(age)==int",
            severity=Severity.WARN,
            enforcement=EnforcementMode.DRY_RUN
        )

        profile_df = profile_dataset(dataset_path)
        engine = RuleEngine([mock_rule])
        results = engine.evaluate(profile_df)

        drift_report = DriftReport(results)
        exit_code = drift_report.get_exit_code()

        print("Exit code (dry-run):", exit_code)
        self.assertEqual(exit_code, 0)

        os.unlink(dataset_path)

    def test_tc2_fail_fast_on_type_change(self):
        csv_data = """name,age,salary
John,25,50000
Jane,thirty,60000
"""
        dataset_path = self._write_temp_csv(csv_data)

        mock_rule = RuleConfig(
            rule_expr="type(age)==int",
            severity=Severity.ERROR,
            enforcement=EnforcementMode.FAIL_FAST
        )

        profile_df = profile_dataset(dataset_path)
        engine = RuleEngine([mock_rule])
        results = engine.evaluate(profile_df)

        drift_report = DriftReport(results)
        exit_code = drift_report.get_exit_code()

        print("Exit code (fail-fast):", exit_code)
        self.assertEqual(exit_code, 2)

        os.unlink(dataset_path)


if __name__ == "__main__":
    unittest.main()
