class DiffVisualizer:
    def render_diff_report(self, diff_result, format="html"):
        """Render a visual diff report with highlighted regressions"""
        if format == "html":
            return self._render_html_diff(diff_result)
        elif format == "markdown":
            return self._render_markdown_diff(diff_result)
        else:
            return self._render_text_diff(diff_result)
            
    def _render_html_diff(self, diff_result):
        """Generate HTML report with interactive visualizations"""
        # Group regressions by severity
        grouped_regressions = self._group_regressions_by_severity(diff_result.regressions)
        
        # Create report sections
        sections = []
        
        # Summary section
        summary = self._create_summary_section(diff_result, grouped_regressions)
        sections.append(summary)
        
        # Schema changes section
        schema_section = self._create_schema_section(diff_result.schema_changes)
        sections.append(schema_section)
        
        # Field metrics section with regression highlights
        metrics_section = self._create_metrics_section(
            diff_result.field_metrics,
            diff_result.regressions  # Used to highlight rows with regressions
        )
        sections.append(metrics_section)
        
        # Distribution visualization section
        distribution_section = self._create_distribution_section(diff_result.field_metrics)
        sections.append(distribution_section)
        
        return self._combine_sections(sections)