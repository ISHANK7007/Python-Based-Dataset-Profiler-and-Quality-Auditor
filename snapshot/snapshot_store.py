from datetime import datetime
from typing import Any, Dict, Optional

class DiffResult:
    def __init__(self, baseline_id: str, current_id: str, timestamp: datetime):
        self.baseline_id = baseline_id
        self.current_id = current_id
        self.timestamp = timestamp
        self.schema_changes = {}
        self.field_metrics = {}
        self.dataset_metrics = {}
        self.regressions = []

class SnapshotDiffer:
    def __init__(self, regression_detector):
        self.regression_detector = regression_detector

    def diff_snapshots(self, baseline_snapshot: Any, current_snapshot: Any, config: Optional[Dict] = None) -> DiffResult:
        """Generate comprehensive diff between two snapshots with regression highlights"""
        diff_result = DiffResult(
            baseline_id=baseline_snapshot.id,
            current_id=current_snapshot.id,
            timestamp=datetime.now()
        )

        # Schema changes (added/removed/modified fields)
        diff_result.schema_changes = self._diff_schema(
            baseline_snapshot.schema,
            current_snapshot.schema
        )

        # Field-level quality metrics
        diff_result.field_metrics = self._diff_field_metrics(
            baseline_snapshot.metrics,
            current_snapshot.metrics
        )

        # Dataset-level quality metrics
        diff_result.dataset_metrics = self._diff_dataset_metrics(
            baseline_snapshot.metrics,
            current_snapshot.metrics
        )

        # Apply regression detection rules
        diff_result.regressions = self.regression_detector.detect_regressions(
            diff_result, config
        )

        return diff_result

    def _diff_schema(self, baseline_schema: Dict, current_schema: Dict) -> Dict:
        return {
            "added": [col for col in current_schema if col not in baseline_schema],
            "removed": [col for col in baseline_schema if col not in current_schema],
            "modified": [
                col for col in current_schema
                if col in baseline_schema and current_schema[col] != baseline_schema[col]
            ]
        }

    def _diff_field_metrics(self, baseline_metrics: Dict, current_metrics: Dict) -> Dict:
        return {
            field: {
                "baseline": baseline_metrics.get(field),
                "current": current_metrics.get(field)
            }
            for field in set(baseline_metrics) | set(current_metrics)
        }

    def _diff_dataset_metrics(self, baseline_metrics: Dict, current_metrics: Dict) -> Dict:
        return {
            "baseline_summary": self._summarize_metrics(baseline_metrics),
            "current_summary": self._summarize_metrics(current_metrics)
        }

    def _summarize_metrics(self, metrics: Dict) -> Dict:
        # Dummy example: summarize overall null rate
        return {
            "null_percentage_avg": sum(
                v.get("null_percentage", 0) for v in metrics.values()
                if isinstance(v, dict)
            ) / max(1, len(metrics))
        }
