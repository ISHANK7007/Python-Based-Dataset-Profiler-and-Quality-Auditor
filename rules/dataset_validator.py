from typing import Dict, Any
import pandas as pd

from rules.audit_policy import AuditPolicy

class DatasetValidator:
    """
    Validates a dataset against rules defined in an AuditPolicy.
    """

    def __init__(self, policy: AuditPolicy):
        self.policy = policy

    def validate(self, dataset_path: str) -> Dict[str, Any]:
        """
        Run rule validation on the dataset.

        Args:
            dataset_path: Path to input dataset (CSV)

        Returns:
            Dict with results including violations
        """
        try:
            df = pd.read_csv(dataset_path)
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to read dataset: {e}",
                "violations": []
            }

        violations = []
        for rule in self.policy.rules:
            result = rule.evaluate(df)
            if not result.passed:
                violations.append({
                    "rule": rule.name,
                    "severity": rule.severity.value,
                    "message": result.message
                })

        return {
            "success": True,
            "violations": violations,
            "num_violations": len(violations),
            "dataset": dataset_path
        }
