from dataclasses import dataclass
from typing import Optional, Dict, Any

from rules.severity_levels import Severity
from rules.enforcement_mode import EnforcementMode

@dataclass
class RuleConfig:
    name: str
    condition: str
    severity: Severity
    message: Optional[str] = None
    enforcement: EnforcementMode = EnforcementMode.ENFORCE
    fail_fast: bool = False
    exit_code: Optional[int] = None
    metadata: Dict[str, Any] = None
