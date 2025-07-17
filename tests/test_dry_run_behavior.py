import pytest
from rules.audit_runner_core import AuditRunner
from rules.rule_config import RuleConfig
from rules.audit_policy import AuditPolicy
from rules.severity_levels import Severity
from rules.enforcement_mode import EnforcementMode

# --- Helper Functions ---

def create_rule(name, condition) -> RuleConfig:
    return RuleConfig(
        name=name,
        condition=condition,
        severity=Severity.ERROR,
        message=f"Violation of {name}",
        enforcement=EnforcementMode.DRY_RUN,
        fail_fast=False,
        exit_code=None,
        metadata={}
    )

def create_test_policy(default_enforcement, rules) -> AuditPolicy:
    return AuditPolicy(
        name="dry_run_test_policy",
        default_enforcement=default_enforcement,
        rules=rules
    )

def create_test_dataset(missing_rate: float = 0.15):
    import pandas as pd
    import tempfile
    import os

    data = {
        "id": [1, 2, 3],
        "column": [None if i < int(3 * missing_rate) else 0.1 for i in range(3)]
    }

    df = pd.DataFrame(data)
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")
    df.to_csv(temp_file.name, index=False)
    return temp_file.name

# --- Actual Test ---

def test_dry_run_mode_report_without_failing():
    """Test that dry-run mode reports issues without failing."""

    # Arrange
    policy = create_test_policy(
        default_enforcement=EnforcementMode.DRY_RUN,
        rules=[create_rule("test_rule", "missing_rate(column) < 0.1")]
    )
    dataset_path = create_test_dataset(missing_rate=0.15)

    # Act
    runner = AuditRunner()
    results = runner.run_audit(dataset_path, policy)

    # Assert
    assert results.get("violations"), "Expected at least one violation"
    assert results["dry_run"] is True
    assert results["violations"][0].get("enforced") is False
    assert results.get("exit_code", 0) == 0  # Should succeed in dry-run
    assert results.get("overall_status", "fail") == "fail"  # Still logically failing
