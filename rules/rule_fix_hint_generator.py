class ExplanationTemplates:
    def __init__(self):
        self.templates = {
            # Template for column removed issue
            "column_removed": {
                "explanation": {
                    "fatal": "CRITICAL: Column '{column}' was removed in {version}. {impact}",
                    "error": "ERROR: Required column '{column}' is missing in {version}.",
                    "warn": "Warning: Optional column '{column}' was removed in {version}.",
                    "info": "Note: Unused column '{column}' was removed in {version}."
                },
                "fix": {
                    "fatal": "This column MUST be restored as it's required for {dependency}.",
                    "error": "Either restore this column or update dependent processes.",
                    "warn": "Consider updating any processes that might use this column.",
                    "info": "No action required."
                }
            },
            # Templates for other violation types
            "distribution_shift": {
                # Similar structure with severity-specific messaging
            }
        }
    
    def get_explanation_template(self, template_key, severity):
        return self.templates.get(template_key, {}).get("explanation", {}).get(
            severity, "Issue detected with {column}"
        )
    
    def get_fix_template(self, template_key, severity):
        return self.templates.get(template_key, {}).get("fix", {}).get(
            severity, "Review and address as appropriate."
        )