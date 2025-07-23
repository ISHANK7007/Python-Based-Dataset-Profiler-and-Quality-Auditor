from typing import List, Dict, Optional
from datetime import datetime


# --- Placeholder Dependencies ---
class DriftSeverity:
    NONE = "none"
    MINOR = "minor"
    MAJOR = "major"
    CRITICAL = "critical"


class DriftPoint:
    def __init__(self, snapshot_id, timestamp, severity, score, metrics, column_details):
        self.snapshot_id = snapshot_id
        self.timestamp = timestamp
        self.severity = severity
        self.score = score
        self.metrics = metrics
        self.column_details = column_details


class DriftTimeline:
    def __init__(self, dataset_id, points, start_date, end_date, metadata):
        self.dataset_id = dataset_id
        self.points = points
        self.start_date = start_date
        self.end_date = end_date
        self.metadata = metadata


# --- Main Processor ---
class DriftTimelineProcessor:
    """Processes snapshot data into a drift timeline."""

    def __init__(self, snapshot_repo, differ):
        self.snapshot_repo = snapshot_repo
        self.differ = differ

    def compute_timeline(self, dataset_id: str, date_range: Optional[tuple] = None,
                         baseline_strategy: str = "first", n_points: Optional[int] = None) -> Optional[DriftTimeline]:
        """Compute a drift timeline for the specified dataset."""
        snapshots = self.snapshot_repo.get_snapshots_in_range(
            dataset_id=dataset_id,
            date_range=date_range,
            limit=n_points
        )

        if not snapshots:
            return None

        sorted_snapshots = sorted(snapshots, key=lambda s: s.timestamp)

        # Determine baseline
        baseline = None
        if baseline_strategy == "first":
            baseline = sorted_snapshots[0]
        elif isinstance(baseline_strategy, str) and baseline_strategy != "previous":
            baseline = self.snapshot_repo.get_snapshot(baseline_strategy)

        drift_points = []

        for i, snapshot in enumerate(sorted_snapshots):
            if baseline_strategy == "first" and i == 0:
                drift_points.append(DriftPoint(
                    snapshot_id=snapshot.id,
                    timestamp=snapshot.timestamp,
                    severity=DriftSeverity.NONE,
                    score=0.0,
                    metrics={},
                    column_details={}
                ))
                continue

            compare_baseline = baseline
            if baseline_strategy == "previous" and i > 0:
                compare_baseline = sorted_snapshots[i - 1]

            if not compare_baseline:
                continue

            drift_result = self.differ.diff_snapshots(compare_baseline, snapshot)

            drift_score, column_details = self._calculate_drift_score(drift_result)
            severity = self._classify_drift_severity(drift_score, drift_result)
            metric_scores = self._extract_metric_scores(drift_result)

            drift_point = DriftPoint(
                snapshot_id=snapshot.id,
                timestamp=snapshot.timestamp,
                severity=severity,
                score=drift_score,
                metrics=metric_scores,
                column_details=column_details
            )

            drift_points.append(drift_point)

        return DriftTimeline(
            dataset_id=dataset_id,
            points=drift_points,
            start_date=sorted_snapshots[0].timestamp,
            end_date=sorted_snapshots[-1].timestamp,
            metadata={
                "baseline_strategy": baseline_strategy,
                "baseline_id": baseline.id if baseline else None,
                "snapshot_count": len(sorted_snapshots)
            }
        )

    def _calculate_drift_score(self, drift_result) -> tuple:
        column_details = {}
        field_scores = []

        for field_name, field_diff in drift_result.field_metrics.items():
            score = 0.0
            if hasattr(field_diff, 'missing_rate_change') and field_diff.missing_rate_change is not None:
                score += abs(field_diff.missing_rate_change) * 10
            if hasattr(field_diff, 'cardinality_change') and field_diff.cardinality_change is not None:
                score += abs(field_diff.cardinality_change) * 5
            if hasattr(field_diff, 'distribution_distance') and field_diff.distribution_distance is not None:
                score += field_diff.distribution_distance * 8

            capped_score = min(1.0, score)
            field_scores.append(capped_score)
            column_details[field_name] = {
                "score": capped_score,
                "metrics": {
                    "missing_rate_change": getattr(field_diff, "missing_rate_change", None),
                    "cardinality_change": getattr(field_diff, "cardinality_change", None),
                    "distribution_distance": getattr(field_diff, "distribution_distance", None)
                }
            }

        overall_score = sum(field_scores) / len(field_scores) if field_scores else 0.0
        return min(1.0, overall_score), column_details

    def _classify_drift_severity(self, drift_score: float, drift_result=None) -> str:
        if drift_score < 0.1:
            return DriftSeverity.NONE
        elif drift_score < 0.3:
            return DriftSeverity.MINOR
        elif drift_score < 0.6:
            return DriftSeverity.MAJOR
        return DriftSeverity.CRITICAL

    def _extract_metric_scores(self, drift_result) -> Dict[str, float]:
        metrics = {}

        if hasattr(drift_result, "schema_changes") and drift_result.schema_changes:
            changed = [c for c in drift_result.schema_changes.values() if getattr(c, "status", "UNCHANGED") != "UNCHANGED"]
            metrics["schema_changes"] = min(1.0, len(changed) / 10)
        else:
            metrics["schema_changes"] = 0.0

        field_metrics = getattr(drift_result, "field_metrics", {})

        if field_metrics:
            def avg_metric(attr, scale):
                vals = [abs(getattr(f, attr, 0) or 0) for f in field_metrics.values()]
                return min(1.0, sum(vals) / len(vals) * scale) if vals else 0.0

            metrics["missing_values"] = avg_metric("missing_rate_change", 10)
            metrics["cardinality"] = avg_metric("cardinality_change", 10)
            metrics["distribution"] = avg_metric("distribution_distance", 5)
        else:
            metrics.update({"missing_values": 0.0, "cardinality": 0.0, "distribution": 0.0})

        return metrics
