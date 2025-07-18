import plotly.graph_objects as go

def _generate_category_drift_chart(self, column_name, baseline_stats, current_stats):
    """Create chart showing category frequency changes between baseline and current."""

    # Extract frequency data safely
    baseline_freqs = baseline_stats.get('unique_values', {}).get('value_counts', {})
    current_freqs = current_stats.get('unique_values', {}).get('value_counts', {})

    # Combine all categories
    all_categories = sorted(set(baseline_freqs.keys()).union(current_freqs.keys()))

    # Prepare count data
    baseline_values = [baseline_freqs.get(cat, 0) for cat in all_categories]
    current_values = [current_freqs.get(cat, 0) for cat in all_categories]

    # Calculate % changes
    pct_changes = []
    for base, curr in zip(baseline_values, current_values):
        if base > 0:
            pct_changes.append(((curr - base) / base) * 100)
        else:
            pct_changes.append(float('inf') if curr > 0 else 0)

    # Create bar chart
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=all_categories,
        y=baseline_values,
        name='Baseline',
        marker_color='blue',
        hovertemplate='%{x}<br>Baseline: %{y}<extra></extra>'
    ))

    fig.add_trace(go.Bar(
        x=all_categories,
        y=current_values,
        name='Current',
        marker_color='red',
        hovertemplate='%{x}<br>Current: %{y}<br>Change: %{customdata:.1f}%<extra></extra>',
        customdata=pct_changes
    ))

    fig.update_layout(
        title=f"Category Frequency Drift: {column_name}",
        xaxis_title="Category",
        yaxis_title="Count",
        barmode='group'
    )

    return fig
