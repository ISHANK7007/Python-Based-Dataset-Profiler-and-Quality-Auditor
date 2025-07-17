from jinja2 import Environment, FileSystemLoader
import os
from visualization.visualization_data_extractor import VisualizationDataExtractor
from visualization.chart_generator import ChartGenerator

class HTMLDashboardGenerator:
    def __init__(self, baseline_profile, current_profile=None, template_dir="templates"):
        self.extractor = VisualizationDataExtractor(baseline_profile, current_profile)
        self.chart_generator = ChartGenerator(self.extractor)
        self.is_drift_mode = current_profile is not None
        self.template_dir = template_dir

    def generate_dashboard(self):
        template = self._load_template()

        charts = {}
        column_names = self._get_column_names()

        for column in column_names:
            fig = self.chart_generator.generate_column_visualization(column)
            charts[column] = self._serialize_chart(fig)

        summary = self._generate_summary_metrics()

        return template.render(
            is_drift_mode=self.is_drift_mode,
            summary=summary,
            charts=charts
        )

    def _serialize_chart(self, fig):
        """Convert Plotly figure to embeddable HTML fragment"""
        return fig.to_html(include_plotlyjs='cdn', full_html=False)

    def _get_column_names(self):
        """Retrieve columns available for visualization"""
        return self.extractor.get_visualizable_columns()

    def _generate_summary_metrics(self):
        """Compute summary statistics or drift counts (optional)"""
        return self.extractor.get_summary_statistics()

    def _load_template(self):
        """Load the Jinja2 template used to render the HTML dashboard"""
        env = Environment(loader=FileSystemLoader(self.template_dir))
        return env.get_template("dashboard_template.html")
