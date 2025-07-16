import os
import sys
import json
from datetime import datetime
from profiler.profiler_entrypoint import profile_dataset
from drift.drift_auditor import analyze_dataset_drift
from cli.cli_exit_codes import ExitCode  # Make sure this Enum exists or define it

def run_drift_audit(args):
    """
    Execute the drift audit command with the provided arguments.
    Returns:
        ExitCode: Return code indicating success or specific error.
    """
    try:
        # Ensure output directory
        if not args.print_to_stdout and not os.path.exists(args.output_dir):
            os.makedirs(args.output_dir)

        # Generate report name
        if args.output_name:
            report_name = args.output_name
        else:
            baseline_name = os.path.splitext(os.path.basename(args.baseline_dataset))[0]
            current_name = os.path.splitext(os.path.basename(args.current_dataset))[0]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_name = f"drift_report_{baseline_name}_to_{current_name}_{timestamp}"

        # Column inclusion/exclusion
        include_columns = [col.strip() for col in args.include_columns.split(',')] if args.include_columns else None
        exclude_columns = [col.strip() for col in args.exclude_columns.split(',')] if args.exclude_columns else None

        # Load thresholds if specified
        thresholds = None
        if args.thresholds:
            with open(args.thresholds, 'r') as f:
                thresholds = json.load(f)

        # Load and profile datasets
        baseline_profile = profile_dataset(
            args.baseline_dataset,
            sample_size=args.sample,
            include_columns=include_columns,
            exclude_columns=exclude_columns
        )
        current_profile = profile_dataset(
            args.current_dataset,
            sample_size=args.sample,
            include_columns=include_columns,
            exclude_columns=exclude_columns
        )

        # Run audit
        drift_report = analyze_dataset_drift(
            baseline_profile,
            current_profile,
            thresholds=thresholds,
            similarity_threshold=args.similarity_threshold,
            visualize=args.visualize and not args.no_visualize
        )

        if args.title:
            drift_report.metadata['report_title'] = args.title

        # Output formats
        formats = ['markdown', 'json', 'html', 'excel'] if args.format == 'all' else [args.format]
        for fmt in formats:
            if args.print_to_stdout and fmt in ['markdown', 'json', 'text']:
                if fmt in ['markdown', 'text']:
                    print(drift_report.to_markdown())
                elif fmt == 'json':
                    print(drift_report.to_json())
            else:
                output_path = os.path.join(args.output_dir, f"{report_name}.{get_extension(fmt)}")
                with open(output_path, 'w', encoding="utf-8") if fmt in ['markdown', 'json', 'text', 'html'] else None as f:
                    if fmt == 'markdown':
                        f.write(drift_report.to_markdown())
                    elif fmt == 'json':
                        f.write(drift_report.to_json())
                    elif fmt == 'html':
                        f.write(drift_report.to_html())
                    elif fmt == 'text':
                        f.write(drift_report.to_text())
                    elif fmt == 'excel':
                        drift_report.to_excel(output_path)

        if not args.quiet and not args.print_to_stdout:
            print_summary(drift_report, args.summary_only)

        return determine_exit_code(drift_report, args.exit_on_drift)

    except Exception as e:
        if not args.quiet:
            print(f"Error: {str(e)}", file=sys.stderr)
        return ExitCode.FAILURE


def determine_exit_code(drift_report, exit_on_drift):
    """Determine appropriate exit code based on severity."""
    summary = drift_report.summary.get('drift_by_severity', {})
    type_summary = drift_report.summary.get('drift_by_type', {})
    findings = drift_report.findings.get('schema_drift', {'major': [], 'moderate': []})

    if type_summary.get('schema', 0) > 0 and (findings['major'] or findings['moderate']):
        if exit_on_drift in ['schema', 'major', 'moderate', 'minor']:
            return ExitCode.CRITICAL

    if summary.get('major', 0) > 0 and exit_on_drift in ['major', 'moderate', 'minor']:
        return ExitCode.ERROR

    if summary.get('moderate', 0) > 0 and exit_on_drift in ['moderate', 'minor']:
        return ExitCode.WARNING

    if summary.get('minor', 0) > 0 and exit_on_drift == 'minor':
        return ExitCode.WARNING

    return ExitCode.SUCCESS


def get_extension(format_name):
    """Map format to file extension."""
    return {
        'markdown': 'md',
        'json': 'json',
        'html': 'html',
        'excel': 'xlsx',
        'text': 'txt'
    }.get(format_name, 'txt')


def print_summary(drift_report, summary_only=False):
    """
    Print formatted drift summary and optional key findings.
    """
    print("\n" + "=" * 80)
    print(" DATASET DRIFT AUDIT SUMMARY")
    print("=" * 80)

    metadata = drift_report.metadata
    summary = drift_report.summary
    print(f"\nBaseline: {metadata.get('baseline_dataset', '-')}")
    print(f"Current:  {metadata.get('current_dataset', '-')}")
    print(f"Time:     {metadata.get('analysis_timestamp', '-')}")

    print("\nDRIFT SUMMARY:")
    print(f"  Total Columns:      {summary.get('total_columns_analyzed', 0)}")
    print(f"  Columns With Drift: {summary.get('total_columns_with_drift', 0)}")

    print("\nSEVERITY BREAKDOWN:")
    for severity, label in [('major', 'Major'), ('moderate', 'Moderate'), ('minor', 'Minor')]:
        count = summary.get('drift_by_severity', {}).get(severity, 0)
        print(f"  {label}: {count}")

    print("\nDRIFT TYPE BREAKDOWN:")
    for drift_type, label in [('schema', 'Schema'), ('distribution', 'Distribution'), ('data_quality', 'Data Quality')]:
        count = summary.get('drift_by_type', {}).get(drift_type, 0)
        print(f"  {label}: {count}")

    if not summary_only:
        print("\nKEY FINDINGS:")
        for severity in ['major', 'moderate']:
            findings = []
            for drift_type, drifts in drift_report.findings.items():
                for finding in drifts.get(severity, []):
                    findings.append((drift_type, finding))
            if findings:
                print(f"\n{severity.upper()} DRIFT:")
                for drift_type, finding in findings[:5]:
                    print(f"  • {finding['column']}: {finding['description']}")
                if len(findings) > 5:
                    print(f"  ... and {len(findings) - 5} more {severity} findings")

    print("\nReports saved to:", metadata.get('output_location', '[not specified]'))
    print("=" * 80 + "\n")
