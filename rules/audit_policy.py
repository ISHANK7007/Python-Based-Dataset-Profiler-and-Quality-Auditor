from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any

from rules.rule_config import RuleConfig
from rules.severity_levels import Severity
from rules.enforcement_mode import EnforcementMode
from rules.thresholds import ThresholdConfig
from rules.schema_compatibility import SchemaCompatibilityConfig

@dataclass
class AuditPolicy:
    """
    Central configuration object for data quality auditing.
    """
    name: str
    description: Optional[str] = None
    version: str = "1.0"
    rules: List[RuleConfig] = field(default_factory=list)
    thresholds: ThresholdConfig = field(default_factory=ThresholdConfig)
    schema_compatibility: SchemaCompatibilityConfig = field(default_factory=SchemaCompatibilityConfig)
    default_enforcement: EnforcementMode = EnforcementMode.ENFORCE
    enable_fail_fast: bool = True
    default_exit_codes: Dict[str, int] = field(default_factory=lambda: {
        "success": 0,
        "warning": 1,
        "error": 2,
        "fatal": 3,
        "rule_failure": 4,
        "system_error": 5,
        "fail_fast": 2
    })
    extends: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, config: Dict[str, Any]) -> "AuditPolicy":
        """Create a policy from a dictionary representation."""
        # Parse rules
        rules = []
        for rule_dict in config.get('rules', []):
            rule = RuleConfig(
                name=rule_dict['name'],
                condition=rule_dict['condition'],
                severity=Severity(rule_dict.get('severity', 'error')),
                message=rule_dict.get('message'),
                enforcement=EnforcementMode(rule_dict.get('enforcement', config.get('default_enforcement', 'enforce'))),
                fail_fast=rule_dict.get('fail_fast', False),
                exit_code=rule_dict.get('exit_code'),
                metadata=rule_dict.get('metadata', {})
            )
            rules.append(rule)

        # Load thresholds and schema config
        thresholds = ThresholdConfig.from_dict(config.get('thresholds', {}))
        schema_compatibility = SchemaCompatibilityConfig.from_dict(config.get('schema_compatibility', {}))

        # Load custom exit codes
        default_exit_codes = {
            "success": 0,
            "warning": 1,
            "error": 2,
            "fatal": 3,
            "rule_failure": 4,
            "system_error": 5,
            "fail_fast": 2
        }
        if 'default_exit_codes' in config:
            default_exit_codes.update(config['default_exit_codes'])

        return cls(
            name=config['name'],
            description=config.get('description'),
            version=config.get('version', '1.0'),
            rules=rules,
            thresholds=thresholds,
            schema_compatibility=schema_compatibility,
            default_enforcement=EnforcementMode(config.get('default_enforcement', 'enforce')),
            enable_fail_fast=config.get('enable_fail_fast', True),
            default_exit_codes=default_exit_codes,
            extends=config.get('extends'),
            metadata=config.get('metadata', {})
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert policy to dictionary representation."""
        rules_dict = [
            {
                'name': rule.name,
                'condition': rule.condition,
                'severity': rule.severity.value,
                'message': rule.message,
                'enforcement': rule.enforcement.value,
                'fail_fast': rule.fail_fast,
                'exit_code': rule.exit_code,
                'metadata': rule.metadata
            } for rule in self.rules
        ]

        return {
            'name': self.name,
            'description': self.description,
            'version': self.version,
            'default_enforcement': self.default_enforcement.value,
            'enable_fail_fast': self.enable_fail_fast,
            'default_exit_codes': self.default_exit_codes,
            'rules': rules_dict,
            'thresholds': self.thresholds.to_dict(),
            'schema_compatibility': self.schema_compatibility.to_dict(),
            'metadata': self.metadata,
            'extends': self.extends
        }

    def get_exit_code(self, violation_severity: Severity, fail_fast: bool = False, custom_exit_code: Optional[int] = None) -> int:
        """
        Get the appropriate exit code based on violation severity and rule configuration.
        """
        if custom_exit_code is not None:
            return custom_exit_code
        if fail_fast:
            return self.default_exit_codes.get("fail_fast", 2)

        severity_map = {
            Severity.INFO: "success",
            Severity.WARN: "warning",
            Severity.ERROR: "error",
            Severity.FATAL: "fatal"
        }
        key = severity_map.get(violation_severity, "error")
        return self.default_exit_codes.get(key, 2)
