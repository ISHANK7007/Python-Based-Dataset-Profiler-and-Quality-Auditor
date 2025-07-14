from rules.rule_explanation_templates import DefaultTemplates
from rules.impact_heuristics import assess_impact

class ExplanationService:
    def __init__(self, templates_repository=None):
        self.templates = templates_repository or DefaultTemplates()

    def annotate_violation(self, violation, profile_context, drift_context=None):
        """
        Add human explanation, severity and fix suggestion to violation

        Args:
            violation: The rule violation object
            profile_context: Contains baseline and current profile information
            drift_context: Contains drift analysis results if available
        """
        metadata = {**violation.details}

        if profile_context:
            metadata.update(self._extract_profile_metadata(violation, profile_context))

        if drift_context:
            metadata.update(self._extract_drift_metadata(violation, drift_context))

        metadata.update(self._assess_impact(violation, profile_context, drift_context))
        metadata.update(self._generate_examples(violation, profile_context, drift_context))

        template_key = self._get_template_key(violation)
        severity = violation.severity or "MEDIUM"

        violation.human_explanation = self._generate_explanation(template_key, severity, metadata)
        violation.fix_suggestion = self._suggest_fix(template_key, severity, metadata)

        return violation

    def _extract_profile_metadata(self, violation, profile_context):
        column = violation.details.get('column')
        stats = profile_context.current.get_column_stats(column) if column else {}
        return {
            "mean": stats.get("mean"),
            "std": stats.get("std"),
            "missing_rate": stats.get("missing_rate"),
            "distinct_count": stats.get("distinct_count"),
            "profile_type": stats.get("type"),
        }

    def _extract_drift_metadata(self, violation, drift_context):
        column = violation.details.get('column')
        drift_info = drift_context.get(column, {}) if column else {}
        return {
            "drift_score": drift_info.get("drift_score"),
            "drift_type": drift_info.get("type"),
            "p_value": drift_info.get("p_value"),
        }

    def _assess_impact(self, violation, profile_context, drift_context):
        from rules.impact_heuristics import assess_impact  # Assumes you define this separately
        rules = profile_context.rules if hasattr(profile_context, "rules") else []
        return assess_impact(violation, profile_context, rules)

    def _generate_examples(self, violation, profile_context, drift_context):
        column = violation.details.get("column")
        try:
            values = profile_context.current.get_column_sample(column)[:3]
            return {"example_values": values}
        except Exception:
            return {"example_values": []}

    def _get_template_key(self, violation):
        return violation.violation_type or "generic"

    def _generate_explanation(self, template_key, severity, metadata):
        try:
            template = self.templates.get_explanation_template(template_key, severity)
            return template.format(**metadata)
        except Exception:
            return "No explanation available."

    def _suggest_fix(self, template_key, severity, metadata):
        try:
            template = self.templates.get_fix_template(template_key, severity)
            return template.format(**metadata)
        except Exception:
            return "No fix suggestion available."
