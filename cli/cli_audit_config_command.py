import click
from collections import defaultdict

from rules.audit_policy_manager import load_historical_results  # Adjust import path as needed

@click.command()
@click.option("--config", "-c", type=click.Path(exists=True), help="Path to audit config (currently unused)")
@click.option("--days", "-d", type=int, default=14, help="Number of past days to analyze")
def dry_run_impact(config, days):
    """Analyze the historical impact of enforcing dry-run audit checks."""
    try:
        results = load_historical_results(days)

        stats = {
            "total_runs": len(results),
            "would_block": sum(1 for r in results if r.get("would_block")),
            "block_rate": sum(1 for r in results if r.get("would_block")) / max(1, len(results)),
            "rules": defaultdict(lambda: {"violations": 0, "runs": 0})
        }

        # Tally per-rule stats
        for result in results:
            for violation in result.get("violations", []):
                rule_name = violation.get("rule", "unknown")
                stats["rules"][rule_name]["violations"] += 1
                stats["rules"][rule_name]["runs"] = stats["total_runs"]

        # Compute violation rates
        for rule_name, rule_stats in stats["rules"].items():
            rule_stats["violation_rate"] = rule_stats["violations"] / max(1, rule_stats["runs"])

        # Print summary
        click.echo(f"\n🔍 Dry Run Impact Analysis (Last {days} days)")
        click.echo(f"Total Runs: {stats['total_runs']}")
        click.echo(f"Would Block: {stats['would_block']} ({stats['block_rate']:.1%})")

        click.echo("\n📊 Rule Impact:")
        for rule_name, rule_stats in sorted(stats["rules"].items(), key=lambda x: x[1]["violation_rate"], reverse=True):
            click.echo(f"  {rule_name}: {rule_stats['violations']} violations ({rule_stats['violation_rate']:.1%})")

        click.echo("\n📌 Recommended Actions:")
        for rule_name, rule_stats in stats["rules"].items():
            rate = rule_stats["violation_rate"]
            if rate > 0.8:
                click.echo(f"  ⚠️  Rule '{rule_name}' is failing in {rate:.1%} of runs. Consider relaxing thresholds.")
            elif rate < 0.05:
                click.echo(f"  ✅  Rule '{rule_name}' is ready for enforcement (low failure rate: {rate:.1%})")

    except Exception as e:
        click.secho(f"Error during dry-run impact analysis: {e}", fg="red", err=True)
        raise SystemExit(1)
