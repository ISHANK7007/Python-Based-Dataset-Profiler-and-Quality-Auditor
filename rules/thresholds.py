from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class ThresholdConfig:
    max_missing: float = 0.05
    max_drift_severity: str = "minor"

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ThresholdConfig":
        return cls(
            max_missing=data.get("max_missing", 0.05),
            max_drift_severity=data.get("max_drift_severity", "minor")
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "max_missing": self.max_missing,
            "max_drift_severity": self.max_drift_severity
        }
