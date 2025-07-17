import plotly.graph_objects as go
import pandas as pd
import base64
from io import BytesIO
from jinja2 import Environment, FileSystemLoader

# Chart generator module
class DriftChartGenerator:
    def generate_missing_values_chart(self, baseline, current, columns):
        missing_baseline = baseline[columns].isnull().mean()
        missing_current = current[columns].isnull().mean()

        fig = go.Figure(data=[
            go.Bar(name='Baseline', x=columns, y=missing_baseline),
            go.Bar(name='Current', x=columns, y=missing_current)
        ])
        fig.update_layout(barmode='group', title='Missing Values Comparison')
        return self._fig_to_base64(fig)

    def generate_distribution_chart(self, baseline, current, column):
        fig = go.Figure()
        fig.add_trace(go.Histogram(x=baseline[column], name='Baseline', opacity=0.6))
        fig.add_trace(go.Histogram(x=current[column], name='Current', opacity=0.6))
        fig.update_layout(barmode='overlay', title=f'Distribution Comparison: {column}')
        return self._fig_to_base64(fig)

    def generate_category_drift_chart(self, baseline, current, column):
        baseline_counts = baseline[column].value_counts(normalize=True)
        current_counts = current[column].value_counts(normalize=True)
        categories = list(set(baseline_counts.index) | set(current_counts.index))

        fig = go.Figure(data=[
            go.Bar(name='Baseline', x=categories, y=[baseline_counts.get(cat, 0) for cat in categories]),
            go.Bar(name='Current', x=categories, y=[current_counts.get(cat, 0) for cat in categories])
        ])
        fig.update_layout(barmode='group', title=f'Category Distribution: {column}')
        return self._fig_to_base64(fig)

    def _fig_to_base64(self, fig):
        buffer = BytesIO()
        fig.write_image(buffer, format='png')
        encoded = base64.b64encode(buffer.getvalue()).decode()
        return f"data:image/png;base64,{encoded}"

# HTML report generator
class HTMLReportGenerator:
    def __init__(self, template_path):
        env = Environment(loader=FileSystemLoader(template_path))
        self.template = env.get_template("report_template.html")
        self.chart_generator = DriftChartGenerator()
    
    def generate_report(self, validation_report, baseline_profile, current_profile):
        charts = {}
        for violation in validation_report.get('violations', []):
            if 'drift' in violation['rule']['name']:
                column = self.extract_column_from_rule(violation)
                charts[column] = self.generate_appropriate_chart(
                    baseline_profile, current_profile, column
                )

        return self.template.render(
            report=validation_report,
            charts=charts
        )

    def generate_appropriate_chart(self, baseline, current, column):
        if pd.api.types.is_numeric_dtype(baseline[column]):
            return self.chart_generator.generate_distribution_chart(baseline, current, column)
        else:
            return self.chart_generator.generate_category_drift_chart(baseline, current, column)

    def extract_column_from_rule(self, violation):
        rule_str = violation['rule']['name']
        # Assuming rule name format: "drift:column_name"
        return rule_str.split(':')[-1].strip()
