class ReportRenderer:
    def __init__(self, context, output_format='html', config=None):
        self.context = context
        self.output_format = output_format
        self.config = config or {}

    def render(self):
        if self.output_format == 'html':
            return self._render_html()
        elif self.output_format == 'markdown':
            return self._render_markdown()
        else:
            raise ValueError(f"Unsupported output format: {self.output_format}")

    def _render_html(self):
        html = [f"<html><head><title>Data Quality Report</title></head><body>"]
        html.append(f"<h1>Report: {self.context.dataset_name}</h1>")

        html.append("<h2>Summary</h2><ul>")
        for k, v in self.context.get_summary().items():
            html.append(f"<li><strong>{k}</strong>: {v}</li>")
        html.append("</ul>")

        if self.context.violations:
            html.append("<h2>Violations</h2>")
            for v in self.context.violations:
                html.append(f"<p><strong>{v.rule_id}</strong> ({v.severity})<br>")
                html.append(f"✦ {v.human_explanation}<br>")
                html.append(f"🔧 {getattr(v, 'fix_suggestion', '')}</p>")

        html.append("</body></html>")
        return "\n".join(html)

    def _render_markdown(self):
        md = [f"# Report: {self.context.dataset_name}\n", "## Summary"]
        for k, v in self.context.get_summary().items():
            md.append(f"- **{k}**: {v}")
        if self.context.violations:
            md.append("\n## Violations")
            for v in self.context.violations:
                md.append(f"- **{v.rule_id}** ({v.severity})")
                md.append(f"  - ✦ {v.human_explanation}")
                md.append(f"  - 🔧 {getattr(v, 'fix_suggestion', '')}")
        return "\n".join(md)
