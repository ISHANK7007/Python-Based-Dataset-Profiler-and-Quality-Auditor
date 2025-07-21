from typing import List, Dict, Optional


class Regression:
    def __init__(self, type: str, field: str, message: str, severity: str, change_value: Optional[float] = None):
        self.type = type
        self.field = field
        self.message = message
        self.severity = severity
        self.change_value = change_value

    def __repr__(self):
        return f"<{self.severity}: {self.type} on '{self.field}' - {self.message}>"


class RegressionDetector:
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or self._default_config()

    def _default_config(self) -> Dict:
        return {
            "allow_field_removal": False,
            "missing_rate_threshold": 0.05,   # 5% increase
            "cardinality_loss_threshold": 0.1 # 10% drop
        }

    def detect_regressions(self, diff_result, override_config: Optional[Dict] = None) -> List[Regression]:
        """Identify regressions in diff results based on configured thresholds."""
        config = override_config or self.config
        regressions = []

        # Schema regressions
        for field_name, schema_change in diff_result.schema_changes.items():
            if hasattr(schema_change, "status") and schema_change.status == "REMOVED" and not config.get("allow_field_removal", False):
                regressions.append(Regression(
                    type="SCHEMA",
                    field=field_name,
                    message=f"Field {field_name} was removed",
                    severity="ERROR"
                ))

        # Field-level regressions
        for field_name, field_diff in diff_result.field_metrics.items():
            # Missing value increase
            if field_diff.missing_rate_change is not None and field_diff.missing_rate_change > 0:
                threshold = config.get("missing_rate_threshold", 0.05)
                if field_diff.missing_rate_change > threshold:
                    severity = "ERROR" if field_diff.missing_rate_change >= 0.1 else "WARNING"
                    regressions.append(Regression(
                        type="MISSING_VALUES",
                        field=field_name,
                        message=f"Missing values increased by {field_diff.missing_rate_change:.2%}",
                        severity=severity,
                        change_value=field_diff.missing_rate_change
                    ))

            # Cardinality drop
            if field_diff.cardinality_change is not None and field_diff.cardinality_change < 0:
                threshold = config.get("cardinality_loss_threshold", 0.1)
                if abs(field_diff.cardinality_change) > threshold:
                    regressions.append(Regression(
                        type="CARDINALITY",
                        field=field_name,
                        message=f"Cardinality decreased by {abs(field_diff.cardinality_change):.2%}",
                        severity="WARNING",
                        change_value=field_diff.cardinality_change
                    ))

            # Removed categories
            if hasattr(field_diff, "removed_categories") and field_diff.removed_categories:
                severity = "ERROR" if len(field_diff.removed_categories) >= 3 else "WARNING"
                regressions.append(Regression(
                    type="CATEGORIES",
                    field=field_name,
                    message=f"Removed categories: {', '.join(field_diff.removed_categories)}",
                    severity=severity
                ))

        return sorted(regressions, key=lambda r: {"INFO": 0, "WARNING": 1, "ERROR": 2, "FATAL": 3}[r.severity], reverse=True)
