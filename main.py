import os
import sys
import argparse

from profiler.profiler_entrypoint import profile_dataset
from visualization.report_context import ReportContext
from visualization.report_renderer_extended import ReportRenderer  # updated to support Markdown
from rules.audit_runner_core import AuditRunner
from rules.audit_policy_manager import AuditPolicyManager
from rules.audit_policy import AuditPolicy


def main():
    parser = argparse.ArgumentParser(description="Run Dataset Profiler and Audit Validator")
    parser.add_argument("file", help="Path to dataset file (.csv)")
    parser.add_argument("--summary", action="store_true", help="Print profile summary only")
    parser.add_argument("--output", help="Path to save profile output (JSON)")
    parser.add_argument("--audit-policy", help="Path to audit policy file (.yaml)")
    parser.add_argument("--output-report", help="Path to save visual report")
    parser.add_argument("--output-format", choices=["html", "markdown"], default="html", help="Report format")
    parser.add_argument("--chart-preset", choices=["minimal", "basic", "standard", "comprehensive"], default="standard")
    parser.add_argument("--no-charts", action="store_true", help="Disable charts in visual report")
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
        for k, v in profile.get_summary().items():
            print(f"{k}: {v}")
    else:
        print("\n=== Full Profile ===")
        print(profile.to_json())

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(profile.to_json())
        print(f"[INFO] Profile saved to: {args.output}")

    # === Policy-Based Audit (NEW) ===
    violations = []
    audit_results = {}
    if args.audit_policy:
        if not os.path.exists(args.audit_policy):
            print(f"[ERROR] Audit policy file not found: {args.audit_policy}")
            sys.exit(1)

        try:
            print(f"\n[INFO] Running audit with policy → {args.audit_policy}")
            manager = AuditPolicyManager()
            policy = manager.get_policy(args.audit_policy)
            runner = AuditRunner()
            audit_results = runner.run_audit(args.file, policy)

            violations = audit_results.get("violations", [])
            print(f"[INFO] Violations found: {len(violations)}")
            for v in violations:
                print(f"- Rule: {v['rule']} | Severity: {v['severity']} | Enforced: {v.get('enforced', True)}")

            if runner.should_fail(audit_results, policy):
                print("[FAIL] Audit did not pass enforcement rules ❌")
            else:
                print("[PASS] Audit passed or violations were in dry-run mode ✅")

        except Exception as e:
            print(f"[ERROR] Audit failed: {e}")
            sys.exit(2)

    # === Visual Report Generation ===
    if args.output_report:
        print(f"[INFO] Generating visual report → {args.output_report}")
        chart_level_map = {
            "minimal": "low",
            "basic": "medium",
            "standard": "medium",
            "comprehensive": "high"
        }
        chart_detail_level = "none" if args.no_charts else chart_level_map.get(args.chart_preset, "medium")

        context = ReportContext(
            baseline_profile=profile,
            current_profile=None,
            violations=violations
        )

        renderer = ReportRenderer(
            output_format=args.output_format
        )

        report = renderer.render_report(audit_results or profile.to_dict(), context={"dry_run": audit_results.get("dry_run", False)})
        with open(args.output_report, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"[SUCCESS] Report saved to {args.output_report}")


if __name__ == "__main__":
    main()
