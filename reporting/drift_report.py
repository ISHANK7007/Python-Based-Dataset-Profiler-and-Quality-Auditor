from enum import Enum
from dataclasses import dataclass
from typing import List, Optional


class ExitCode(Enum):
    SUCCESS = 0
    SCHEMA_DRIFT = 1
    TYPE_MISMATCH = 2
    UNKNOWN_ERROR = 3


@dataclass
class DriftResult:
    message: str
    severity: str = "info"


class DriftReport:
    def __init__(self, drift_detected: bool = False, exit_code: ExitCode = ExitCode.SUCCESS):
        self.drift_detected = drift_detected
        self.exit_code = exit_code
        self.violations: List[DriftResult] = []

    def add_violation(self, message: str, severity: str = "warn"):
        self.violations.append(DriftResult(message=message, severity=severity))
        if severity == "fatal":
            self.exit_code = ExitCode.TYPE_MISMATCH
        elif severity == "warn" and self.exit_code == ExitCode.SUCCESS:
            self.exit_code = ExitCode.SCHEMA_DRIFT

    def get_exit_code(self) -> int:
        return self.exit_code.value

    def to_text(self) -> str:
        lines = ["Drift Report Summary:"]
        for v in self.violations:
            lines.append(f"- [{v.severity.upper()}] {v.message}")
        return "\n".join(lines)
