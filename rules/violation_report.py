# Extend existing violation objects
class RuleViolation:
    def __init__(self, rule_id, details, violation_type):
        self.rule_id = rule_id
        self.details = details  # e.g., {'field': 'age', 'missing_rate': 0.45}
        self.violation_type = violation_type  # e.g., "missing_values", "outliers", "drift"
        self.severity = None  # Will be populated: "HIGH", "MEDIUM", "LOW"
        self.human_explanation = None  # Human-readable explanation
        self.fix_suggestion = None  # Suggestion to fix

# Default template generator (fallback)
class DefaultTemplates:
    def get_explanation(self, violation_type, details):
        if violation_type == "missing_values":
            return f"Field '{details.get('field')}' has a high missing rate ({details.get('missing_rate')*100:.1f}%)."
        elif violation_type == "drift":
            return f"Field '{details.get('field')}' shows significant distributional drift."
        elif violation_type == "outliers":
            return f"Field '{details.get('field')}' contains extreme values that deviate from the norm."
        else:
            return "Unrecognized violation type."

    def get_fix_hint(self, violation_type, details):
        if violation_type == "missing_values":
            return "Consider imputing missing values or excluding the field if it's not critical."
        elif violation_type == "drift":
            return "Review upstream data changes or retrain model with recent data."
        elif violation_type == "outliers":
            return "Apply outlier detection and treatment such as capping or transformation."
        else:
            return "No suggestion available."

# Explanation service
class ExplanationService:
    def __init__(self, templates_repository=None):
        self.templates = templates_repository or DefaultTemplates()

    def annotate_violation(self, violation):
        """Add human explanation, severity and fix suggestion to violation"""
        violation.severity = self._determine_severity(violation)
        violation.human_explanation = self._generate_explanation(violation)
        violation.fix_suggestion = self._suggest_fix(violation)
        return violation

    def _determine_severity(self, violation):
        # Simplified severity logic based on violation type and detail thresholds
        if violation.violation_type == "missing_values":
            rate = violation.details.get("missing_rate", 0)
            if rate > 0.5:
                return "HIGH"
            elif rate > 0.2:
                return "MEDIUM"
            else:
                return "LOW"
        elif violation.violation_type == "drift":
            score = violation.details.get("drift_score", 0)
            if score > 0.7:
                return "HIGH"
            elif score > 0.4:
                return "MEDIUM"
            else:
                return "LOW"
        elif violation.violation_type == "outliers":
            count = violation.details.get("outlier_count", 0)
            if count > 50:
                return "HIGH"
            elif count > 10:
                return "MEDIUM"
            else:
                return "LOW"
        return "MEDIUM"

    def _generate_explanation(self, violation):
        return self.templates.get_explanation(violation.violation_type, violation.details)

    def _suggest_fix(self, violation):
        return self.templates.get_fix_hint(violation.violation_type, violation.details)
