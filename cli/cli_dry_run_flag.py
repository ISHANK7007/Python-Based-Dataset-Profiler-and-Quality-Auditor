import sys
import click

from rules.audit_runner_core import run_validation
from rules.audit_policy_manager import determine_exit_code
from visualization.report_renderer_extended import ReportRenderer
from cli.cli_violation_explainer import output_results  # adjust if placed elsewhere

@click.command()
@click.option("--dry-run", is_flag=True, default=False,
              help="Report issues but exit with success code (0) regardless of violations")
@click.option("--output-file", type=click.Path(), default=None,
              help="Path to write the rendered report output")
@click.option("--output-format", type=click.Choice(["text", "html", "markdown", "json"]), default="text",
              help="Format of the report output")
def validate(dry_run, output_file, output_format):
    """Validate a dataset against rules."""
    try:
        # Run validation
        results = run_validation()

        # Determine exit code for actual enforcement mode
        standard_exit_code = determine_exit_code(results)

        # Handle output
        if output_file:
            with open(output_file, "w") as f:
                renderer = ReportRenderer(output_format)
                report = renderer.render_report(results, {"dry_run": dry_run})
                f.write(report)
        else:
            if dry_run:
                click.secho("⚠️  DRY RUN MODE - Issues reported but not enforced", fg="yellow", bold=True)

            output_results(results, format=output_format)

            if dry_run and standard_exit_code > 0:
                click.secho(
                    f"⚠️  In enforcement mode, this would have failed with exit code: {standard_exit_code}",
                    fg="yellow"
                )

        # Exit handling
        sys.exit(0 if dry_run else standard_exit_code)

    except Exception as e:
        click.secho(f"Error during validation: {e}", fg="red", err=True)
        sys.exit(1)
