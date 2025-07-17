import os
from typing import List, Optional

from rules.audit_policy import AuditPolicy  # Ensure this path is correct

class AuditPolicyManager:
    """
    Manages loading, resolving, and caching audit policies.
    Handles inheritance and provides access to effective policies.
    """

    def __init__(self, policy_dirs: Optional[List[str]] = None):
        """
        Initialize the policy manager.

        Args:
            policy_dirs: List of directories to search for policies
        """
        self.policy_dirs = policy_dirs or ["./policies", "./audit"]
        self._policy_cache = {}  # Cache for loaded policies

    def get_policy(self, policy_name_or_path: str,
                   environment: Optional[str] = None,
                   dataset: Optional[str] = None) -> AuditPolicy:
        """
        Get a policy by name or path, resolving inheritance if needed.

        Args:
            policy_name_or_path: Policy name or file path
            environment: Optional environment to apply (dev, prod, etc.)
            dataset: Optional dataset name for dataset-specific settings

        Returns:
            Resolved AuditPolicy instance
        """
        # If it's a direct file path
        if os.path.isfile(policy_name_or_path):
            policy = AuditPolicy.from_file(policy_name_or_path)
        else:
            policy = self._find_policy_by_name(policy_name_or_path)

        # Handle inheritance
        if getattr(policy, "extends", None):
            base_policy = self.get_policy(policy.extends)
            policy = base_policy.merge(policy)

        # Apply environment and dataset customization
        return policy.get_effective_policy(environment, dataset)

    def _find_policy_by_name(self, policy_name: str) -> AuditPolicy:
        """
        Find policy by name in configured directories.

        Args:
            policy_name: Logical name of policy file (without extension)

        Returns:
            AuditPolicy instance if found

        Raises:
            ValueError if policy is not found
        """
        if policy_name in self._policy_cache:
            return self._policy_cache[policy_name]

        for directory in self.policy_dirs:
            for ext in ['.yaml', '.yml', '.json']:
                path = os.path.join(directory, f"{policy_name}{ext}")
                if os.path.isfile(path):
                    policy = AuditPolicy.from_file(path)
                    self._policy_cache[policy_name] = policy
                    return policy

        raise ValueError(f"Policy not found in configured paths: {policy_name}")

    def list_policies(self) -> List[str]:
        """
        List all available policies from configured directories.

        Returns:
            Sorted list of policy names (without extensions)
        """
        policies = set()
        for directory in self.policy_dirs:
            if not os.path.isdir(directory):
                continue

            for filename in os.listdir(directory):
                if filename.endswith(('.yaml', '.yml', '.json')):
                    policy_name = os.path.splitext(filename)[0]
                    policies.add(policy_name)

        return sorted(policies)
