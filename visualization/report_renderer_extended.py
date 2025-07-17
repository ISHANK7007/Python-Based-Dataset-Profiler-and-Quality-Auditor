from typing import Dict, Any

from visualization.template_strategy import HtmlTemplateStrategy, MarkdownTemplateStrategy

class ReportRenderer:
    """
    Renders audit reports in different formats using strategy pattern.
    Supports HTML and Markdown output formats.
    """

    def __init__(self, output_format: str = "html"):
        self.strategies = {
            "html": HtmlTemplateStrategy(),
            "markdown": MarkdownTemplateStrategy()
        }

        if output_format not in self.strategies:
            raise ValueError(f"Unsupported output format: {output_format}")

        self.strategy = self.strategies[output_format]

    def render_report(self, validation_results: Dict[str, Any], context: Dict[str, Any] = None,
                      template_name: str = "report.j2") -> str:
        """
        Render the validation report in the selected format.

        Args:
            validation_results: Dict containing audit results
            context: Additional rendering context (e.g., dry-run mode)
            template_name: Template file to use (optional)

        Returns:
            Rendered string report
        """
        context = context or {}
        template_data = self._prepare_template_data(validation_results, context)
        return self.strategy.render(template_data, template_name)

    def _prepare_template_data(self, validation_results: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Common data preparation for rendering.

        Args:
            validation_results: Raw audit output
            context: Supplementary metadata (e.g., dry-run indicator)

        Returns:
            Dict ready for template rendering
        """
        return {
            "summary": self._build_summary(validation_results),
            "violations": self._process_violations(validation_results),
            "stats": self._process_statistics(validation_results),
            "context": context
        }

    def _build_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate high-level summary info from results."""
        return {
            "dataset": results.get("dataset", "unknown"),
            "violations": len(results.get("violations", [])),
            "dry_run": results.get("dry_run", False)
        }

    def _process_violations(self, results: Dict[str, Any]) -> Any:
        """Process violation list for rendering."""
        return results.get("violations", [])

    def _process_statistics(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Extract any extra statistics (placeholder for now)."""
        return {
            "num_rules_checked": len(results.get("rules_checked", [])) if "rules_checked" in results else "n/a"
        }
