import plotly.graph_objects as go

def _generate_distribution_comparison(self, column_name, baseline_stats, current_stats):
    """Create overlaid distribution chart comparing baseline and current profiles."""
    
    baseline_dist = baseline_stats.get('distribution', {})
    current_dist = current_stats.get('distribution', {})
    
    # Validate presence of histogram data
    if all(key in baseline_dist for key in ['histogram_bins', 'histogram_counts']) and \
       all(key in current_dist for key in ['histogram_bins', 'histogram_counts']):
        
        fig = go.Figure()

        # Baseline histogram
        fig.add_trace(go.Bar(
            x=baseline_dist['histogram_bins'],
            y=baseline_dist['histogram_counts'],
            name='Baseline',
            opacity=0.6,
            marker_color='blue'
        ))

        # Current histogram
        fig.add_trace(go.Bar(
            x=current_dist['histogram_bins'],
            y=current_dist['histogram_counts'],
            name='Current',
            opacity=0.6,
            marker_color='red'
        ))

        # Add mean lines
        baseline_mean = baseline_stats.get('basic_stats', {}).get('mean')
        current_mean = current_stats.get('basic_stats', {}).get('mean')

        if baseline_mean is not None:
            fig.add_vline(
                x=baseline_mean,
                line_dash="dash",
                line_color="blue",
                annotation_text="Baseline Mean",
                annotation_position="top left"
            )
        if current_mean is not None:
            fig.add_vline(
                x=current_mean,
                line_dash="dash",
                line_color="red",
                annotation_text="Current Mean",
                annotation_position="top right"
            )

        fig.update_layout(
            title=f"Distribution Comparison: {column_name}",
            xaxis_title=column_name,
            yaxis_title="Frequency",
            barmode='overlay'
        )

        return fig

    # Fallback if histogram data is missing
    return self._generate_stats_comparison(column_name, baseline_stats, current_stats)
