import os
from datetime import datetime
from jinja2 import Environment, FileSystemLoader, select_autoescape

class ReportRenderer:
    """
    Renders data quality reports in various formats (HTML, Markdown) based on
    profile data, violations, and configuration options.
    """

    def __init__(self, report_context, output_format='html', config=None):
        self.context = report_context
        self.format = output_format.lower()
        self.config = config or {}

        # Default configuration
        self.default_config = {
            'chart_mode': 'auto',
            'highlight_severity': 'warn',
            'expand_severity': 'error',
            'max_categories': 10,
            'theme': 'light',
            'include_passed_rules': False,
            'chart_detail_level': 'medium',
            'include_charts': True
        }

        for key, value in self.default_config.items():
            if key not in self.config:
                self.config[key] = value

        self._init_chart_generator()
        if self.format == 'html':
            self._init_template_engine()

    def render(self):
        if self.format == 'html':
            return self._render_html()
        elif self.format == 'markdown':
            return self._render_markdown()
        else:
            raise ValueError(f"Unsupported output format: {self.format}")

    def _render_html(self):
        template_context = {
            'title': self._get_report_title(),
            'summary': self._generate_summary_data(),
            'violations': self._group_violations_by_severity(),
            'columns': self._prepare_column_analysis(),
            'metadata': self._prepare_metadata(),
            'config': self.config,
            'charts': self._generate_all_charts(),
            'css': self._get_css_styles()
        }
        return self.template_engine.get_template("report.html").render(template_context)

    def _render_markdown(self):
        md_parts = [f"# {self._get_report_title()}", "", "## Summary"]
        summary_data = self._generate_summary_data()
        md_parts += [
            f"- **Dataset**: {summary_data['dataset_name']}",
            f"- **Timestamp**: {summary_data['timestamp']}",
            f"- **Status**: {summary_data['status']}", ""
        ]

        md_parts.append("## Violations")
        for severity, violations in self._group_violations_by_severity().items():
            if violations:
                md_parts.append(f"### {severity.title()} Level Violations\n")
                md_parts.append("| Rule | Column | Expected | Actual | Explanation |")
                md_parts.append("|------|--------|----------|--------|-------------|")
                for v in violations:
                    md_parts.append(f"| {v['rule']['name']} | {v['column']} | {v['result']['expected']} | "
                                    f"{v['result']['actual']} | {self._generate_explanation(v)} |")
                md_parts.append("")
        if self.config.get('include_charts'):
            md_parts.append("## Charts\n*Note: Charts are available in the HTML version of this report.*\n")
        return "\n".join(md_parts)

    def _init_chart_generator(self):
        mode = self.config['chart_mode']
        if mode == 'auto':
            mode = 'static' if os.environ.get('CI') else 'interactive'
        if mode == 'interactive':
            from visualization.chart_generator import ChartGenerator as PlotlyChartGenerator
            self.chart_generator = PlotlyChartGenerator(self.context)
        else:
            from visualization.chart_generator import ChartGenerator as MatplotlibChartGenerator
            self.chart_generator = MatplotlibChartGenerator(self.context)

    def _init_template_engine(self):
        self.template_engine = Environment(
            loader=FileSystemLoader("templates"),
            autoescape=select_autoescape(['html', 'xml'])
        )
        self.template_engine.filters['format_number'] = lambda x: f"{x:,}"
        self.template_engine.filters['format_percent'] = lambda x: f"{x:.2%}"

    def _get_report_title(self):
        if self.context.is_drift_report:
            return f"Drift Report: {self.context.current_profile.name} vs {self.context.baseline_profile.name}"
        else:
            return f"Data Quality Report: {self.context.baseline_profile.name}"

    def _generate_summary_data(self):
        counts = {'fatal': 0, 'error': 0, 'warn': 0, 'info': 0, 'total': 0}
        for v in self.context.violations:
            sev = v['rule']['severity'].lower()
            if sev in counts:
                counts[sev] += 1
                counts['total'] += 1
        status = 'Passed'
        status_class = 'success'
        if counts['fatal'] > 0:
            status = 'Failed (Fatal)'
            status_class = 'fatal'
        elif counts['error'] > 0:
            status = 'Failed (Error)'
            status_class = 'error'
        elif counts['warn'] > 0:
            status = 'Warning'
            status_class = 'warn'
        return {
            'dataset_name': self.context.current_profile.name,
            'baseline_name': self.context.baseline_profile.name if self.context.is_drift_report else None,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'violations': counts,
            'status': status,
            'status_class': status_class,
            'columns_analyzed': len(self.context.columns),
            'rows_analyzed': self.context.current_profile.row_count,
            'is_drift_report': self.context.is_drift_report,
        }

    def _group_violations_by_severity(self):
        result = {'fatal': [], 'error': [], 'warn': [], 'info': []}
        for v in self.context.violations:
            sev = v['rule']['severity'].lower()
            if sev in result:
                enhanced = v.copy()
                enhanced['explanation'] = self._generate_explanation(v)
                enhanced['chart_id'] = self._get_chart_id(v)
                result[sev].append(enhanced)
        return result

    def _generate_explanation(self, violation):
        rule = violation['rule']
        result = violation['result']
        col = violation.get('column', 'dataset')
        explanation = f"The rule '{rule['name']}' for {col} was violated. "
        explanation += f"Expected {result['expected']}, but got {result['actual']}."
        return explanation

    def _prepare_column_analysis(self):
        columns = {}
        for col in self.context.columns:
            violations = [v for v in self.context.violations if v.get('column') == col]
            stats = self._get_column_statistics(col)
            highest = 'pass'
            for v in violations:
                s = v['rule']['severity'].lower()
                if self._get_severity_rank(s) > self._get_severity_rank(highest):
                    highest = s
            columns[col] = {
                'name': col,
                'violations': violations,
                'statistics': stats,
                'highest_severity': highest,
                'charts': self._get_chart_ids_for_column(col)
            }
        return columns

    def _prepare_metadata(self):
        return {
            'generated_at': self.context.timestamp,
            'tool_version': self.context.tool_version,
            'rules_file': self.context.rules_file,
            'command': self.context.command_line
        }

    def _generate_all_charts(self):
        charts = {}
        for v in self.context.violations:
            chart_id = self._get_chart_id(v)
            charts[chart_id] = self._generate_chart_for_violation(v)
        for col in self.context.columns:
            charts[f"distribution-{self._sanitize_id(col)}"] = self.chart_generator.generate_distribution_chart(col)
        return charts

    def _generate_chart_for_violation(self, violation):
        col = violation.get('column')
        if not col:
            return self._generate_generic_violation_chart(violation)
        rule = violation['rule']['name'].lower()
        if 'missing' in rule:
            return self.chart_generator.generate_missing_values_chart(col)
        elif 'distribution' in rule or 'mean' in rule:
            return self.chart_generator.generate_distribution_chart(col)
        elif 'category' in rule:
            return self.chart_generator.generate_category_chart(col)
        else:
            return self.chart_generator.generate_generic_chart(col)

    def _generate_generic_violation_chart(self, violation):
        import plotly.graph_objects as go
        fig = go.Figure()
        fig.add_trace(go.Indicator(
            mode="number",
            value=1,
            title={"text": "Generic Violation Chart"}
        ))
        return fig

    def _get_chart_id(self, violation):
        return f"violation-{self._sanitize_id(violation['rule']['name'])}-{self._sanitize_id(violation.get('column', 'dataset'))}"

    def _get_chart_ids_for_column(self, column):
        return [
            f"distribution-{self._sanitize_id(column)}"
        ]

    def _sanitize_id(self, text):
        import re
        return re.sub(r'[^a-zA-Z0-9]', '-', str(text)).lower()

    def _get_column_statistics(self, column):
        return self.context.current_profile.get_column_statistics(column)

    def _get_severity_rank(self, severity):
        ranks = {'pass': 0, 'info': 1, 'warn': 2, 'error': 3, 'fatal': 4}
        return ranks.get(severity.lower(), 0)

    def _get_css_styles(self):
        return self._get_light_theme_css()

    def _get_light_theme_css(self):
        return """
        :root {
            --bg-color: #ffffff;
            --text-color: #333333;
            --header-bg: #f5f5f5;
            --border-color: #dddddd;
            --fatal-color: #D32F2F;
            --error-color: #F44336;
            --warn-color: #FFC107;
            --info-color: #2196F3;
            --pass-color: #4CAF50;
        }
        """
