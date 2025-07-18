import unittest

class RuleViolation:
    def __init__(self, rule_id, details, violation_type):
        self.rule_id = rule_id
        self.details = details
        self.violation_type = violation_type
        self.severity = None
        self.human_explanation = None
        self.fix_suggestion = None

class DefaultTemplates:
    def get_explanation_template(self, key, severity):
        if key == "outliers":
            return "Age column mean exceeds expected threshold"
        elif key == "drift":
            return "Field {column} removed from schema"
        return "No explanation available"

    def get_fix_template(self, key, severity):
        if key == "outliers":
            return "Consider capping age values or removing outliers"
        elif key == "drift":
            return "Ensure this removal is intentional or update rule expectations"
        return "No suggestion available"

class ExplanationService:
    def __init__(self, templates_repository=None):
        self.templates = templates_repository or DefaultTemplates()

    def annotate_violation(self, violation, profile_context=None, drift_context=None):
        key = violation.violation_type
        severity = violation.severity or "HIGH"
        metadata = violation.details
        if drift_context and violation.details.get("column") in drift_context:
            metadata.update(drift_context.get(violation.details["column"]))
        violation.human_explanation = self.templates.get_explanation_template(key, severity).format(**metadata)
        violation.fix_suggestion = self.templates.get_fix_template(key, severity).format(**metadata)
        return violation

class TestViolationExplanationRealWorld(unittest.TestCase):

    def setUp(self):
        self.explainer = ExplanationService()

    def test_mean_age_rule_violation(self):
        violation = RuleViolation(
            rule_id="RULE001",
            details={"column": "age", "mean": 57.1},
            violation_type="outliers"
        )
        violation.severity = "HIGH"
        self.explainer.annotate_violation(violation)

        print("\n[TC1] Mean Age Violation:")
        print("Explanation:", violation.human_explanation)
        print("Fix Suggestion:", violation.fix_suggestion)

        self.assertIn("Age", violation.human_explanation)
        self.assertIn("exceeds", violation.human_explanation)
        self.assertIn("capping", violation.fix_suggestion)
        self.assertIn("outliers", violation.fix_suggestion)

    def test_email_field_removed_schema_drift(self):
        violation = RuleViolation(
            rule_id="SCHEMA001",
            details={"column": "email"},
            violation_type="drift"
        )
        violation.severity = "HIGH"
        drift_context = {
            "email": {"type": "removed"}
        }

        self.explainer.annotate_violation(violation, drift_context=drift_context)

        print("\n[TC2] Email Field Removed:")
        print("Explanation:", violation.human_explanation)
        print("Fix Suggestion:", violation.fix_suggestion)

        self.assertIn("email", violation.human_explanation.lower())
        self.assertIn("removed", violation.human_explanation.lower())
        self.assertIn("intentional", violation.fix_suggestion.lower())
        self.assertIn("update", violation.fix_suggestion.lower())

if __name__ == "__main__":
    unittest.main()
