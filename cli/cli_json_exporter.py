import datetime

class SchemaValidationReport:
    """
    Generate a comprehensive Markdown report on schema validation and changes.
    """
    
    def __init__(self, schema_comparer):
        self.comparison = schema_comparer.schema_changes
        self.baseline = schema_comparer.baseline
        self.current = schema_comparer.current
    
    def generate_markdown_report(self):
        """
        Generate a detailed Markdown report on schema changes.
        """
        report = [
            "# Schema Change Report",
            "",
            f"**Baseline Dataset:** {self.baseline.dataset_name}",
            f"**Current Dataset:** {self.current.dataset_name}",
            f"**Timestamp:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## Summary",
            ""
        ]
        
        # Safe access for comparison keys
        type_changes = self.comparison.get('type_changes', {})
        missing_columns = self.comparison.get('missing_columns', [])
        new_columns = self.comparison.get('new_columns', [])
        potential_renames = self.comparison.get('potential_renames', [])

        total_changes = (
            len(type_changes) +
            len(missing_columns) +
            len(new_columns) +
            len(potential_renames)
        )
        
        report.append(f"**Total Changes:** {total_changes}")
        report.append(f"**Type Changes:** {len(type_changes)}")
        report.append(f"**Missing Columns:** {len(missing_columns)}")
        report.append(f"**New Columns:** {len(new_columns)}")
        report.append(f"**Potential Renames:** {len(potential_renames)}")
        report.append("")

        if type_changes:
            report.append("## Type Changes\n")
            report.append("| Column | Baseline Type | Current Type |")
            report.append("| ------ | ------------- | ------------- |")
            for col, type_info in type_changes.items():
                report.append(f"| {col} | {type_info['baseline_type']} | {type_info['current_type']} |")
            report.append("")

        if missing_columns:
            report.append("## Missing Columns\n")
            report.append("These columns exist in the baseline dataset but are missing in the current dataset:\n")
            for col in missing_columns:
                col_profile = self.baseline.get_column_profile(col)
                report.append(f"- **{col}** ({col_profile.inferred_type})")
            report.append("")

        if new_columns:
            report.append("## New Columns\n")
            report.append("These columns exist in the current dataset but were not in the baseline:\n")
            for col in new_columns:
                col_profile = self.current.get_column_profile(col)
                report.append(f"- **{col}** ({col_profile.inferred_type})")
            report.append("")

        if potential_renames:
            report.append("## Potential Renamed Columns\n")
            report.append("| Original Name | New Name | Confidence | Evidence |")
            report.append("| ------------- | --------- | ---------- | -------- |")
            for old_col, new_col, confidence, evidence in potential_renames:
                evidence_str = "<br>".join(evidence)
                report.append(f"| {old_col} | {new_col} | {confidence:.2f} | {evidence_str} |")
            report.append("")

        return "\n".join(report)
