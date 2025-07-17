import click
from rules.audit_runner_core import run_validation
from visualization.report_renderer_extended import generate_markdown_summary

@click.command()
@click.option('--summary-file', help='Path to output Markdown summary for PR comments')
def validate(summary_file):
    """
    Runs the validation logic and optionally writes a Markdown summary to the given file.
    """
    try:
        results = run_validation()

        if summary_file:
            generate_markdown_summary(results, summary_file)
            click.echo(f"Markdown summary written to: {summary_file}")
        else:
            click.echo("Validation completed without summary output.")

    except Exception as e:
        click.echo(f"Validation failed: {e}", err=True)
        raise SystemExit(1)
