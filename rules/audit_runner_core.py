import os
from typing import Union, Dict, Any, Optional

from rules.audit_policy import AuditPolicy, EnforcementMode, Severity
from rules.audit_policy_manager import AuditPolicyManager
from rules.dataset_validator import DatasetValidator
from visualization.report_renderer_extended import ReportRenderer

class AuditRunner:
    """
    Runs data quality audits using AuditPolicy configurations.
    Supports both CLI and programmatic use cases.
    """

    def __init__(self, policy_manager: Optional[AuditPolicyManager] = None):
        """
        Initialize the audit runner.

        Args:
            policy_manager: Optional AuditPolicyManager instance
        """
        self.policy_manager = policy_manager or AuditPolicyManager()

    def run_audit(self,
                  dataset_path: str,
                  policy: Union[str, AuditPolicy],
                  environment: Optional[str] = None,
                  output_format: str = "text",
                  output_file: Optional[str] = None) -> Dict[str, Any]:
        """
        Run an audit using the specified policy.

        Args:
            dataset_path: Path to dataset
            policy: Policy name, path, or AuditPolicy instance
            environment: Optional environment name (dev, prod, etc.)
            output_format: Output format (text, json, html, markdown)
            output_file: Optional file to write results

        Returns:
            Audit results dictionary
        """
        # Resolve policy from name or path
        if isinstance(policy, str):
            resolved_policy = self.policy_manager.get_policy(
                policy,
                environment=environment,
                dataset=os.path.basename(dataset_path)
            )
        else:
            resolved_policy = policy

        # Validate dataset
        validator = DatasetValidator(resolved_policy)
        results = validator.validate(dataset_path)

        # Determine if audit is in dry-run mode
        results['dry_run'] = resolved_policy.default_enforcement != EnforcementMode.ENFORCE

        # Mark violations as dry-run if needed
        for violation in results.get('violations', []):
            rule_name = violation.get('rule')
            rule = next((r for r in resolved_policy.rules if r.name == rule_name), None)
            if rule and rule.enforcement != EnforcementMode.ENFORCE:
                violation['enforced'] = False
                violation['dry_run'] = True

        # Write output if requested
        if output_file:
            renderer = ReportRenderer(output_format)
            report = renderer.render_report(results)
            with open(output_file, "w") as f:
                f.write(report)

        return results

    def should_fail(self, results: Dict[str, Any], policy: AuditPolicy) -> bool:
        """
        Determine if the audit should result in failure (non-zero exit).

        Args:
            results: Audit results dictionary
            policy: AuditPolicy instance

        Returns:
            True if audit should fail based on violations, else False
        """
        # Always succeed in dry-run mode
        if policy.default_enforcement != EnforcementMode.ENFORCE:
            return False

        for violation in results.get("violations", []):
            rule_name = violation.get("rule")
            severity = violation.get("severity")

            rule = next((r for r in policy.rules if r.name == rule_name), None)
            if rule and rule.enforcement != EnforcementMode.ENFORCE:
                continue

            if severity in (Severity.ERROR.value, Severity.FATAL.value):
                return True

        return False
