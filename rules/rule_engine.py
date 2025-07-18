
import yaml
from rules.rule_evaluator import RuleEvaluator

def validate_dataset_against_rules(profile, rule_file_path):
    """
    Load rules from YAML and validate them against the dataset profile.

    Args:
        profile (DatasetProfile): Profile object with summary stats.
        rule_file_path (str): Path to YAML rule file.

    Returns:
        (bool, list): (True, []) if all pass; else (False, list of violations)
    """
    with open(rule_file_path, "r") as f:
        rule_defs = yaml.safe_load(f)

    evaluator = RuleEvaluator()
    summary = profile.get_summary()
    violations = []

    for rule_obj in rule_defs.get("rules", []):
        rule_str = rule_obj["rule"]
        severity = rule_obj.get("severity", "error")

        try:
            if not evaluator.evaluate(rule_str, summary):
                violations.append({
                    "rule": rule_str,
                    "severity": severity,
                    "message": "Rule failed"
                })
        except Exception as e:
            violations.append({
                "rule": rule_str,
                "severity": "fatal",
                "message": f"Rule evaluation error: {str(e)}"
            })

    passed = len(violations) == 0
    return passed, violations
