# rule_expectation_engine.py

import yaml
from rules.expectations import (
    NullPercentageExpectation,  # ensure these classes are implemented or stubbed
    ComparativeExpectation,
    ValidationResult,
    ValidationReport
)

class ExpectationLoader:
    def load_from_yaml(self, yaml_path):
        """Load expectations from a YAML file."""
        with open(yaml_path, "r") as f:
            config = yaml.safe_load(f)

        self._validate_config_schema(config)

        expectations = []
        for exp_config in config.get("expectations", []):
            exp = self._create_expectation(exp_config)
            expectations.append(exp)

        return expectations

    def _validate_config_schema(self, config):
        if "expectations" not in config or not isinstance(config["expectations"], list):
            raise ValueError("Invalid configuration: 'expectations' list is required.")

    def _create_expectation(self, config):
        exp_type = config.get("type")
        if exp_type == "column":
            return NullPercentageExpectation(
                column_name=config["column"],
                threshold=config["threshold"],
                operator=config.get("operator", "<=")
            )
        else:
            raise ValueError(f"Unsupported expectation type: {exp_type}")


class ExpectationValidator:
    def __init__(self, exit_on_failure=False):
        self.exit_on_failure = exit_on_failure

    def validate_dataset(self, current_profile, expectations, snapshot_repository=None):
        results = []

        for expectation in expectations:
            if isinstance(expectation, ComparativeExpectation):
                if snapshot_repository is None:
                    results.append(ValidationResult(
                        is_valid=None,
                        expectation=expectation,
                        message="Comparative expectation skipped - no snapshot repository available"
                    ))
                    continue
                result = expectation.validate(current_profile, snapshot_repository)
            else:
                result = expectation.validate(current_profile)

            results.append(result)

            if self.exit_on_failure and result.is_valid is False:
                break

        return ValidationReport(results)
