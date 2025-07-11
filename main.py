import os
import sys
import argparse
from profiler.profiler_entrypoint import profile_dataset

# Safe import with fallback
try:
    from rules.rule_engine import validate_dataset_against_rules
    RULES_ENABLED = True
except ImportError as e:
    print(f"[WARNING] Rule validation is disabled due to import error: {e}")
    validate_dataset_against_rules = None
    RULES_ENABLED = False

def main():
    parser = argparse.ArgumentParser(description="Run Dataset Profiler and optionally validate rules.")
    parser.add_argument("file", help="Path to the dataset file (.csv)")
    parser.add_argument("--summary", action="store_true", help="Print summary of profiling")
    parser.add_argument("--output", help="Save profile output to JSON file")
    parser.add_argument("--rules", help="Path to rule YAML file for validation")
    args = parser.parse_args()

    if not os.path.exists(args.file):
        print(f"[ERROR] File not found: {args.file}")
        sys.exit(1)

    print(f"[INFO] Profiling: {args.file}")
    try:
        profile = profile_dataset(args.file)
    except Exception as e:
        print(f"[ERROR] Failed to profile file: {e}")
        sys.exit(1)

    if args.summary:
        print("\n=== Dataset Summary ===")
        for key, val in profile.get_summary().items():
            print(f"{key}: {val}")
    else:
        print("\n=== Full Profile ===")
        print(profile.to_json())

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(profile.to_json())
        print(f"\n[INFO] Profile saved to: {args.output}")

    # Rule validation block
    if args.rules:
        if not RULES_ENABLED:
            print("[WARNING] Skipping rule validation (rule engine not available)")
            return

        if not os.path.exists(args.rules):
            print(f"[ERROR] Rules file not found: {args.rules}")
            sys.exit(1)

        print(f"\n[INFO] Validating dataset against rules: {args.rules}")
        try:
            passed, violations = validate_dataset_against_rules(profile, args.rules)
            if passed:
                print("[SUCCESS] All rules passed ✅")
            else:
                print("[FAIL] Rule violations detected ❌")
                for v in violations:
                    print(f"- Rule: {v['rule']}  |  Severity: {v['severity']}  |  Message: {v['message']}")
                sys.exit(2)
        except Exception as e:
            print(f"[ERROR] Rule evaluation failed: {e}")
            sys.exit(2)

if __name__ == "__main__":
    main()
