import unittest

class MockDriftReport:
    def __init__(self, drift_dict):
        self.drift = drift_dict

    def get_column_drift(self, column):
        return self.drift.get(column, None)

    @staticmethod
    def compare_snapshots(v1, v2):
        drift_result = {}

        if "age" in v1["columns"] and "age" in v2["columns"]:
            v1_age = v1["columns"]["age"]
            v2_age = v2["columns"]["age"]
            null_drift = v2_age["null_percentage"] - v1_age["null_percentage"]
            mean_drift = v2_age["mean"] - v1_age["mean"]
            severity = "error" if null_drift > 0.07 and mean_drift > 5 else "warn"

            drift_result["age"] = {
                "null_percentage_drift": null_drift,
                "mean_drift": mean_drift,
                "severity": severity
            }

        if "status" in v1["columns"] and "status" in v2["columns"]:
            v1_cats = set(v1["columns"]["status"]["categories"])
            v2_cats = set(v2["columns"]["status"]["categories"])
            added = list(v2_cats - v1_cats)
            severity = "warn" if added else "info"

            drift_result["status"] = {
                "type": "categorical",
                "added_categories": added,
                "delta_lineage": ", ".join(added),
                "severity": severity
            }

        return MockDriftReport(drift_result)


class TestRealWorldDriftAudit(unittest.TestCase):

    def setUp(self):
        self.snapshot_v1 = {
            "timestamp": "2024-06-01T00:00:00",
            "columns": {
                "age": {
                    "null_percentage": 0.04,
                    "mean": 32.5,
                    "data_type": "int"
                },
                "status": {
                    "categories": ["active", "inactive"],
                    "data_type": "string"
                }
            }
        }

        self.snapshot_v2 = {
            "timestamp": "2024-07-01T00:00:00",
            "columns": {
                "age": {
                    "null_percentage": 0.12,
                    "mean": 40.1,
                    "data_type": "int"
                },
                "status": {
                    "categories": ["active", "inactive", "archived", "flagged"],
                    "data_type": "string"
                }
            }
        }

    def test_tc1_numeric_drift_on_age(self):
        """TC1: age column shows significant numeric drift in nulls and mean."""
        report = MockDriftReport.compare_snapshots(self.snapshot_v1, self.snapshot_v2)
        age_drift = report.get_column_drift("age")
        self.assertIsNotNone(age_drift, "Drift not reported for 'age' column")
        self.assertAlmostEqual(age_drift.get("null_percentage_drift", 0), 0.08, delta=0.005, msg="Null increase not detected")
        self.assertGreaterEqual(age_drift.get("mean_drift", 0), 7.0, "Mean increase not detected")
        self.assertEqual(age_drift.get("severity"), "error", "Expected 'error' severity for major drift")

    def test_tc2_categorical_drift_on_status(self):
        """TC2: status column adds new categories."""
        report = MockDriftReport.compare_snapshots(self.snapshot_v1, self.snapshot_v2)
        status_drift = report.get_column_drift("status")
        self.assertIsNotNone(status_drift, "Drift not reported for 'status' column")
        self.assertEqual(status_drift.get("type"), "categorical", "Expected categorical drift type")
        self.assertIn("archived", status_drift.get("added_categories", []), "Missing 'archived' in new categories")
        self.assertIn("flagged", status_drift.get("added_categories", []), "Missing 'flagged' in new categories")
        self.assertEqual(status_drift.get("severity"), "warn", "Expected 'warn' severity for minor categorical drift")

if __name__ == "__main__":
    unittest.main()
