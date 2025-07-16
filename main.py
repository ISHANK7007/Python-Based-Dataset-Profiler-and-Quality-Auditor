import os
import sys
import argparse
from profiler.profiler_entrypoint import profile_dataset
from visualization.report_renderer import ReportRenderer
from visualization.report_context import ReportContext

# Safe import of optional rule engine components
try:
    from rules.rule_engine import validate_dataset_against_rules
    from rules.violation_explanation_logic import ExplanationService
    RULES_ENABLED = True
except ImportError as e:
    print(f"[WARNING] Rule validation is disabled due to import error: {e}")
    validate_dataset_against_rules = None
    ExplanationService = None
    RULES_ENABLED = False


def main():
    parser = argparse.ArgumentParser(description="Run Dataset Profiler and optionally validate rules.")
    parser.add_argument("file", help="Path to the dataset file (.csv)")
    parser.add_argument("--summary", action="store_true", help="Print summary of profiling")
    parser.add_argument("--output", help="Save profile output to JSON file")
    parser.add_argument("--rules", help="Path to rule YAML file for validation")
    parser.add_argument("--output-report", help="Path to save HTML/Markdown report")
    parser.add_argument("--output-format", choices=["html", "markdown"], default="html", help="Report output format")
    parser.add_argument("--chart-preset", choices=["minimal", "basic", "standard", "comprehensive"], default="standard", help="Chart detail level preset")
    parser.add_argument("--no-charts", action="store_true", help="Disable charts in the report")
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

    violations = []
    if args.rules:
        if not RULES_ENABLED:
            print("[WARNING] Skipping rule validation (rule engine not available)")
        elif not os.path.exists(args.rules):
            print(f"[ERROR] Rules file not found: {args.rules}")
            sys.exit(1)
        else:
            print(f"\n[INFO] Validating dataset against rules: {args.rules}")
            try:
                passed, violations = validate_dataset_against_rules(profile, args.rules)

                if ExplanationService:
                    explainer = ExplanationService()
                    for v in violations:
                        explainer.annotate_violation(v, profile_context=profile)

                if passed:
                    print("[SUCCESS] All rules passed ✅")
                else:
                    print("[FAIL] Rule violations detected ❌")
                    for v in violations:
                        print(f"- Rule: {v.rule_id} | Severity: {v.severity}")
                        print(f"  ✦ Explanation: {v.human_explanation}")
                        print(f"  🔧 Fix Suggestion: {v.fix_suggestion}\n")
                    # Continue execution
            except Exception as e:
                print(f"[ERROR] Rule evaluation failed: {e}")
                sys.exit(2)

    # === Visual Report Generation ===
    if args.output_report:
        print(f"[INFO] Generating visual report → {args.output_report}")
        chart_level_map = {
            'minimal': 'low',
            'basic': 'medium',
            'standard': 'medium',
            'comprehensive': 'high'
        }
        chart_detail_level = 'none' if args.no_charts else chart_level_map.get(args.chart_preset, 'medium')

        context = ReportContext(
            baseline_profile=profile,
            current_profile=None,
            violations=violations
        )

        renderer = ReportRenderer(context, output_format=args.output_format, config={
            'chart_detail_level': chart_detail_level,
            'include_charts': not args.no_charts
        })

        report_output = renderer.render()
        with open(args.output_report, "w", encoding="utf-8") as f:
            f.write(report_output)
        print(f"[SUCCESS] Report saved to {args.output_report}")


if __name__ == "__main__":
    main()
