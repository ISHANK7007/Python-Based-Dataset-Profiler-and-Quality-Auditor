import pandas as pd
import plotly.graph_objects as go

class ChartEmbedder:
    def generate_column_chart(self, column, baseline_profile, current_profile):
        baseline = baseline_profile['columns'][column]
        current = current_profile['columns'][column]
        dtype = baseline.get('type', 'unknown')

        if dtype in ['int', 'float', 'number']:
            return self._generate_numeric_chart(column, baseline, current)
        else:
            return self._generate_categorical_chart(column, baseline, current)

    def _generate_numeric_chart(self, column, baseline_stats, current_stats):
        baseline_mean = baseline_stats.get('statistics', {}).get('mean', 0)
        current_mean = current_stats.get('statistics', {}).get('mean', 0)

        fig = go.Figure()
        fig.add_trace(go.Indicator(
            mode="delta",
            value=current_mean,
            delta={
                'reference': baseline_mean,
                'relative': True,
                'valueformat': '.1%',
                'increasing': {'color': 'red'},
                'decreasing': {'color': 'green'}
            },
            title={"text": f"<b>Mean Shift</b><br>{column}"}
        ))
        return fig

    def _generate_categorical_chart(self, column, baseline_stats, current_stats):
        baseline = baseline_stats.get('unique_values', {}).get('value_counts', {})
        current = current_stats.get('unique_values', {}).get('value_counts', {})
        all_cats = list(set(baseline.keys()) | set(current.keys()))
        baseline_vals = [baseline.get(cat, 0) for cat in all_cats]
        current_vals = [current.get(cat, 0) for cat in all_cats]

        fig = go.Figure()
        fig.add_trace(go.Bar(name='Baseline', x=all_cats, y=baseline_vals))
        fig.add_trace(go.Bar(name='Current', x=all_cats, y=current_vals))
        fig.update_layout(barmode='group', title=f"Category Drift: {column}")
        return fig

    def serialize_to_html(self, fig):
        return fig.to_html(full_html=False, include_plotlyjs='cdn')
