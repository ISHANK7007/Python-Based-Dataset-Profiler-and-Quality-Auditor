from visualization.chart_embedder import ChartEmbedder

class HTMLReportGenerator:
    def __init__(self, baseline_profile, current_profile=None, 
                 violations=None, chart_mode="auto"):
        self.baseline = baseline_profile
        self.current = current_profile
        self.violations = violations or []
        self.chart_mode = chart_mode
        self.chart_embedder = ChartEmbedder()

        self.severity_order = ['fatal', 'error', 'warn', 'info']
        self.severity_colors = {
            'fatal': '#D32F2F',
            'error': '#F44336',
            'warn': '#FFC107',
            'info': '#2196F3',
        }

    def generate_report(self):
        html_parts = self._get_html_header()

        # Severity summary section
        html_parts.append(self._generate_severity_summary())

        # Violations grouped by severity
        for severity in self.severity_order:
            html_parts.append(self._generate_violations_section(severity))

        # Column-level analysis with charts
        html_parts.append(self._generate_column_analysis())

        html_parts.append('</body></html>')
        return '\n'.join(html_parts)

    def _get_html_header(self):
        return [
            '<html>',
            '<head><title>Data Drift & Rule Violation Report</title></head>',
            '<body>',
            '<h1>📊 Data Quality Report</h1>'
        ]

    def _generate_severity_summary(self):
        counts = {s: 0 for s in self.severity_order}
        for v in self.violations:
            severity = v.get('severity', 'info')
            if severity in counts:
                counts[severity] += 1
        html = ['<div><h2>Violation Severity Summary</h2><ul>']
        for severity in self.severity_order:
            count = counts[severity]
            if count > 0:
                html.append(f'<li style="color:{self.severity_colors[severity]}">'
                            f'{severity.title()}: {count} issue(s)</li>')
        html.append('</ul></div>')
        return '\n'.join(html)

    def _generate_violations_section(self, severity):
        section = [f'<div><h3 style="color:{self.severity_colors[severity]}">'
                   f'{severity.title()} Violations</h3><ul>']
        for v in self.violations:
            if v.get('severity') == severity:
                rule = v.get('rule', {}).get('name', 'Unnamed Rule')
                explanation = v.get('explanation', '')
                section.append(f'<li><strong>{rule}</strong>: {explanation}</li>')
        section.append('</ul></div>')
        return '\n'.join(section)

    def _generate_column_analysis(self):
        if not self.current:
            return '<p>Drift mode is disabled. Only baseline profile available.</p>'

        html = ['<div><h2>📈 Column-Level Drift Analysis</h2>']
        shared_columns = set(self.baseline['columns'].keys()) & set(self.current['columns'].keys())
        for col in sorted(shared_columns):
            html.append(f'<h4>{col}</h4>')
            try:
                fig = self.chart_embedder.generate_column_chart(col, self.baseline, self.current)
                html.append(self.chart_embedder.serialize_to_html(fig))
            except Exception as e:
                html.append(f'<p>Error generating chart for {col}: {e}</p>')
        html.append('</div>')
        return '\n'.join(html)
