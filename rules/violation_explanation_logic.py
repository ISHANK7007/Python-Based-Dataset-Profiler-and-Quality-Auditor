class DefaultTemplates:
    """Fallback explanation and fix template repository"""

    def get_explanation_template(self, key, severity):
        # Return a default explanation template with severity interpolation
        return {
            "missing_values": {
                "LOW":    "Field '{field}' has a minor missing rate issue.",
                "MEDIUM": "Field '{field}' has a moderate missing rate of {missing_rate:.2%}.",
                "HIGH":   "Field '{field}' has a critical missing rate of {missing_rate:.2%}, which may impact model reliability.",
            },
            "drift": {
                "LOW":    "Minor drift detected in field '{field}'.",
                "MEDIUM": "Moderate drift detected in field '{field}' with drift score {drift_score:.2f}.",
                "HIGH":   "Severe drift detected in field '{field}'. Distribution has significantly changed.",
            },
            "outliers": {
                "LOW":    "A few outliers found in field '{field}'.",
                "MEDIUM": "Field '{field}' has a noticeable number of outliers.",
                "HIGH":   "Field '{field}' has excessive outliers, which may skew results.",
            },
            "generic": {
                "LOW":    "Minor violation in field '{field}'.",
                "MEDIUM": "Moderate issue detected in field '{field}'.",
                "HIGH":   "Serious problem detected in field '{field}'.",
            }
        }.get(key, {}).get(severity, "No explanation available.")

    def get_fix_template(self, key, severity):
        # Return default fix suggestions by severity
        return {
            "missing_values": {
                "LOW":    "No action needed. Optionally impute missing values for '{field}'.",
                "MEDIUM": "Consider imputing missing values or analyzing '{field}' importance.",
                "HIGH":   "Imputation or exclusion of '{field}' is recommended due to high missing rate.",
            },
            "drift": {
                "LOW":    "Monitor changes in '{field}' going forward.",
                "MEDIUM": "Investigate upstream data for '{field}' and consider retraining if needed.",
                "HIGH":   "Review source of drift in '{field}'. Retraining or filtering may be necessary.",
            },
            "outliers": {
                "LOW":    "Log and monitor outliers in '{field}'.",
                "MEDIUM": "Apply winsorization or clipping for outliers in '{field}'.",
                "HIGH":   "Remove or transform extreme outliers in '{field}' to reduce impact.",
            },
            "generic": {
                "LOW":    "No fix required.",
                "MEDIUM": "Review and address issue in '{field}'.",
                "HIGH":   "Immediate attention required for '{field}'.",
            }
        }.get(key, {}).get(severity, "No fix suggestion available.")


class ExplanationService:
    def __init__(self, templates_repository=None):
        self.templates = templates_repository or DefaultTemplates()

    def annotate_violation(self, violation):
        """Add human explanation and fix suggestion to violation based on severity"""
        # Severity should already be set on the violation from the rule
        template_key = self._get_template_key(violation)

        # Generate explanation with appropriate tone based on severity
        violation.human_explanation = self._generate_explanation(
            violation, 
            template_key, 
            severity=violation.severity
        )

        # Generate appropriate action based on severity
        violation.fix_suggestion = self._suggest_fix(
            violation, 
            template_key, 
            severity=violation.severity
        )

        return violation

    def _get_template_key(self, violation):
        """Determine which template to use based on violation type and rule"""
        if hasattr(violation, "rule_id") and violation.rule_id:
            return violation.violation_type or f"rule_{violation.rule_id}"
        elif hasattr(violation, "violation_type"):
            return violation.violation_type
        else:
            return "generic"

    def _generate_explanation(self, violation, template_key, severity):
        try:
            template = self.templates.get_explanation_template(template_key, severity)
            return template.format(**violation.details)
        except Exception:
            return "No explanation available for this violation."

    def _suggest_fix(self, violation, template_key, severity):
        try:
            template = self.templates.get_fix_template(template_key, severity)
            return template.format(**violation.details)
        except Exception:
            return "No fix suggestion available."
