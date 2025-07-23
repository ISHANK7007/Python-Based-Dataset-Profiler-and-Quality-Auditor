from rules.rule_expectation_engine import ExpectationLoader, ExpectationValidator
from cli.cli_rule_exit_handler import apply_exit_logic

def validate_rules_from_config(profile, rule_config_path):
    """
    Load expectations from a YAML config file and validate them using the current profile.
    Applies exit logic if validation fails.
    """
    print(f"[INFO] Loading expectations from {rule_config_path}")
    loader = ExpectationLoader()
    expectations = loader.load_from_yaml(rule_config_path)

    print(f"[INFO] Validating {len(expectations)} expectations against profile")
    validator = ExpectationValidator()
    result = validator.validate_dataset(profile, expectations)

    print(result)

    # Simulate audit_results format to re-use existing exit logic
    audit_results = {
        "failed": not result.is_valid,
        "exit_code": 2 if not result.is_valid else 0
    }
    apply_exit_logic(audit_results, policy={})  # Empty policy fallback

    return audit_results["exit_code"]