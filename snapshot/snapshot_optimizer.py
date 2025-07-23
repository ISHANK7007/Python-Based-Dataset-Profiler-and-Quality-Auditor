from typing import Dict, List, Optional

# === Dummy Repository Stub (Replace with actual implementation) ===
class SnapshotRepository:
    def get_snapshot_metadata(self, snapshot_id):
        return {
            "data_checksum": "checksum_" + snapshot_id,
            "row_count": 1000,
            "file_size_bytes": 204800,
            "last_modified": "2024-07-17T10:00:00"
        }

    def get_snapshot_schema(self, snapshot_id):
        return {"columns": ["age", "status", "income"]}

    def get_snapshot_metrics(self, snapshot_id):
        return {
            "age": {"missing_rate": 0.05, "unique_count": 30},
            "status": {"missing_rate": 0.01, "unique_count": 3}
        }

    def get_snapshot_distributions(self, snapshot_id, columns):
        return {col: {"A": 0.4, "B": 0.6} for col in columns}

class OptimizedDiffer:
    """Optimized differ that avoids loading full dataframes."""

    def compare_snapshots(self, baseline_id: str, current_id: str, config: Optional[Dict] = None) -> Dict:
        repo = SnapshotRepository()

        baseline_meta = repo.get_snapshot_metadata(baseline_id)
        current_meta = repo.get_snapshot_metadata(current_id)

        if baseline_meta.get('data_checksum') == current_meta.get('data_checksum'):
            return self._create_identical_diff_result(baseline_meta, current_meta)

        schema_diff = self._compare_schema(
            repo.get_snapshot_schema(baseline_id),
            repo.get_snapshot_schema(current_id)
        )

        needs_full_comparison = self._needs_full_comparison(schema_diff, baseline_meta, current_meta)

        if needs_full_comparison:
            metrics_diff = self._compare_metrics(
                repo.get_snapshot_metrics(baseline_id),
                repo.get_snapshot_metrics(current_id),
                schema_diff
            )
        else:
            metrics_diff = self._create_empty_metrics_diff()

        if config and config.get('include_distributions', False):
            columns_needing_distributions = self._columns_needing_distributions(metrics_diff)
            if columns_needing_distributions:
                dist_baseline = repo.get_snapshot_distributions(baseline_id, columns_needing_distributions)
                dist_current = repo.get_snapshot_distributions(current_id, columns_needing_distributions)
                distribution_diff = self._compare_distributions(dist_baseline, dist_current)
                metrics_diff = self._merge_distribution_diff(metrics_diff, distribution_diff)

        return self._create_diff_result(baseline_meta, current_meta, schema_diff, metrics_diff)

    def _needs_full_comparison(self, schema_diff: Dict, baseline_meta: Dict, current_meta: Dict) -> bool:
        if self._has_significant_schema_changes(schema_diff):
            return True

        baseline_rows = baseline_meta.get('row_count', 0)
        current_rows = current_meta.get('row_count', 0)
        if baseline_rows == 0 or current_rows == 0:
            return True

        row_diff_pct = abs(current_rows - baseline_rows) / baseline_rows
        if row_diff_pct > 0.01:
            return True

        baseline_size = baseline_meta.get('file_size_bytes', 0)
        current_size = current_meta.get('file_size_bytes', 0)
        if baseline_size == 0 or current_size == 0:
            return True

        size_diff_pct = abs(current_size - baseline_size) / baseline_size
        if size_diff_pct > 0.05:
            return True

        baseline_modified = baseline_meta.get('last_modified')
        current_modified = current_meta.get('last_modified')
        if baseline_modified and current_modified and baseline_modified != current_modified:
            return True

        return False

    def _compare_schema(self, baseline_schema: Dict, current_schema: Dict) -> Dict:
        return {"changed_fields": []}

    def _compare_metrics(self, baseline_metrics: Dict, current_metrics: Dict, schema_diff: Dict) -> Dict:
        return {"field_differences": {}}

    def _compare_distributions(self, baseline_dist: Dict, current_dist: Dict) -> Dict:
        return {"distribution_differences": {}}

    def _merge_distribution_diff(self, metrics_diff: Dict, distribution_diff: Dict) -> Dict:
        metrics_diff.update(distribution_diff)
        return metrics_diff

    def _create_identical_diff_result(self, baseline_meta: Dict, current_meta: Dict) -> Dict:
        return {
            "status": "identical",
            "baseline_meta": baseline_meta,
            "current_meta": current_meta,
            "diff": {}
        }

    def _create_empty_metrics_diff(self) -> Dict:
        return {}

    def _columns_needing_distributions(self, metrics_diff: Dict) -> List[str]:
        return list(metrics_diff.get("field_differences", {}).keys())

    def _create_diff_result(self, baseline_meta: Dict, current_meta: Dict, schema_diff: Dict, metrics_diff: Dict) -> Dict:
        return {
            "baseline": baseline_meta,
            "current": current_meta,
            "schema_diff": schema_diff,
            "metrics_diff": metrics_diff
        }

    def _has_significant_schema_changes(self, schema_diff: Dict) -> bool:
        return bool(schema_diff.get("changed_fields"))
