import pytest
from rules.audit_runner_core import AuditRunner
from rules.rule_config import RuleConfig
from rules.audit_policy import AuditPolicy
from rules.severity_levels import Severity
from rules.enforcement_mode import EnforcementMode

# ---- Helper functions for test setup ----

def create_rule(name, condition, fail_fast=False) -> RuleConfig:
    return RuleConfig(
        name=name,
        condition=condition,
        severity=Severity.FATAL,
        message=f"Violation of {name}",
        enforcement=EnforcementMode.ENFORCE,
        fail_fast=fail_fast,
        exit_code=None,
        metadata={}
    )

def create_test_policy(rules) -> AuditPolicy:
    return AuditPolicy(
        name="fail_fast_test_policy",
        rules=rules,
        enable_fail_fast=True
    )

def create_test_dataset(unique_primary_key=True):
    import pandas as pd
    import tempfile
    import os

    df = pd.DataFrame({
        "id": [1, 2, 2] if not unique_primary_key else [1, 2, 3],
        "column": [0.1, None, 0.3]
    })

    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")
    df.to_csv(temp_file.name, index=False)
    return temp_file.name

# ---- Actual test ----

def test_fail_fast_early_termination():
    """Test that fail-fast rules terminate processing early."""

    # Arrange
    policy = create_test_policy(rules=[
        create_rule("critical_rule", "is_primary_key_unique", fail_fast=True),
        create_rule("non_critical_rule", "missing_rate(column) < 0.1")
    ])
    dataset_path = create_test_dataset(unique_primary_key=False)

    # Act
    runner = AuditRunner()
    results = runner.run_audit(dataset_path, policy)

    # Assert
    assert results.get("terminated_early") is True
    assert results.get("termination_rule") == "critical_rule"
    assert len(results.get("violations", [])) == 1  # Only the fail-fast rule should trigger
