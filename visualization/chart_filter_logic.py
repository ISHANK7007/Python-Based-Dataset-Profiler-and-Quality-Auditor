class DriftReportGenerator:
    def __init__(self, baseline_profile, current_profile, violations):
        self.baseline = baseline_profile
        self.current = current_profile
        self.violations = violations
        self.severity_colors = {
            'fatal': '#D32F2F',
            'error': '#F44336',
            'warn': '#FFC107',
            'info': '#2196F3',
            'pass': '#4CAF50'
        }
        self.severity_icons = {
            'fatal': '❌',
            'error': '⚠️',
            'warn': '⚠️',
            'info': 'ℹ️',
            'pass': '✅'
        }

    def _count_violations_by_severity(self):
        """Aggregate violation counts by severity level"""
        counts = {key: 0 for key in self.severity_colors}
        for violation in self.violations:
            severity = violation.get('severity', 'info')
            if severity in counts:
                counts[severity] += 1
            else:
                counts['info'] += 1  # fallback
        return counts

    def _generate_severity_summary(self):
        """Render a severity summary section as HTML"""
        counts = self._count_violations_by_severity()

        html = ['<div class="severity-summary" style="margin-bottom: 1em;">']
        html.append('<h3>🔎 Violation Severity Summary</h3>')
        html.append('<ul style="list-style: none; padding: 0;">')

        for severity, count in counts.items():
            if count > 0:
                color = self.severity_colors[severity]
                icon = self.severity_icons[severity]
                html.append(f'''
                    <li style="margin: 0.3em 0;">
                        <span style="color: {color}; font-weight: bold;">{icon} {severity.capitalize()}</span>: {count} issue(s)
                    </li>
                ''')

        html.append('</ul></div>')
        return '\n'.join(html)

    def generate_full_html(self):
        """Assemble complete HTML report (can be extended with charts, tables, etc.)"""
        html_parts = []
        html_parts.append('<html><head><title>Drift Report</title></head><body>')
        html_parts.append(self._generate_severity_summary())
        # Add charts, column diffs, tables, etc. here later
        html_parts.append('</body></html>')
        return '\n'.join(html_parts)
