import unittest
import pandas as pd
import tempfile
import os
from collections import defaultdict

class Violation:
    def __init__(self, rule_id, column, severity, message):
        self.rule_id = rule_id
        self.column = column
        self.severity = severity
        self.message = message

def mock_profile_dataset(df):
    profile = {}
    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            profile[col] = {
                "type": "numeric",
                "mean": df[col].mean(),
                "std": df[col].std()
            }
        else:
            profile[col] = {
                "type": "categorical",
                "values": dict(df[col].value_counts())
            }
    return profile

class DriftAuditor:
    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2

    def run(self):
        drift = defaultdict(dict)
        for col in self.p1:
            if col in self.p2 and self.p1[col]["type"] == self.p2[col]["type"]:
                if self.p1[col]["type"] == "numeric":
                    drift[col]["mean_shift"] = abs(self.p1[col]["mean"] - self.p2[col]["mean"])
                elif self.p1[col]["type"] == "categorical":
                    drift[col]["new_categories"] = list(set(self.p2[col]["values"]) - set(self.p1[col]["values"]))
        return drift

class ReportRenderer:
    def __init__(self, baseline_profile, current_profile, violations, chart_mode="standard"):
        self.baseline = baseline_profile
        self.current = current_profile
        self.violations = violations

    def render(self):
        html = "<html><body><h1>Data Quality Report</h1>"
        if "income" in self.baseline and "income" in self.current:
            b = self.baseline["income"]["mean"]
            c = self.current["income"]["mean"]
            html += f"<p>Mean income changed from {b:.2f} to {c:.2f}</p>"
        for v in self.violations:
            html += f"<div>{v.rule_id} - {v.column} - {v.severity}: {v.message}</div>"
        html += "</body></html>"
        return html

class TestVisualReportCases(unittest.TestCase):
    def setUp(self):
        self.v1 = pd.DataFrame({
            "id": [1, 2, 3, 4, 5],
            "income": [100, 105, 98, 103, 99],
            "status": ["approved", "approved", "pending", "approved", "pending"]
        })

        self.v2 = pd.DataFrame({
            "id": [1, 2, 3, 4, 5],
            "income": [200, 210, 220, 215, 205],
            "status": ["approved", "fraudulent", "approved", "fraudulent", "approved"]
        })

        self.p1 = mock_profile_dataset(self.v1)
        self.p2 = mock_profile_dataset(self.v2)

        self.violations = [
            Violation("R001", "status", "error", "Unexpected category: fraudulent")
        ]

    def test_mean_drift_chart_on_income(self):
        print("\nRunning TC1: Mean drift check on income")
        auditor = DriftAuditor(self.p1, self.p2)
        drift = auditor.run()
        self.assertIn("income", drift)
        shift = drift["income"]["mean_shift"]
        print(f"✔ Mean drift detected on 'income': Shift = {shift:.2f}")

        renderer = ReportRenderer(self.p1, self.p2, [])
        html = renderer.render()
        self.assertIn("Mean income", html)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".html", mode="w", encoding="utf-8") as f:
            f.write(html)
            print(f"✔ HTML report written to: {f.name}")

    def test_category_drift_visual_on_status(self):
        print("\nRunning TC2: Unexpected category in 'status'")
        renderer = ReportRenderer(self.p1, self.p2, self.violations)
        html = renderer.render()
        self.assertIn("fraudulent", html.lower())
        print("✔ Violation with 'fraudulent' category correctly highlighted")

        with tempfile.NamedTemporaryFile(delete=False, suffix=".html", mode="w", encoding="utf-8") as f:
            f.write(html)
            print(f"✔ Violation HTML report written to: {f.name}")

if __name__ == "__main__":
    unittest.main()
