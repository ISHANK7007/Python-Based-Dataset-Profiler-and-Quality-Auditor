import pytest
from visualization.report_renderer_extended import ReportRenderer

# --- Mock helper ---

def create_test_results(overall_status="fail", violations=None,
                        terminated_early=False, termination_rule=None):
    return {
        "dataset": "test_dataset.csv",
        "overall_status": overall_status,
        "violations": violations or [],
        "terminated_early": terminated_early,
        "termination_rule": termination_rule,
        "dry_run": False
    }

# --- Actual Test ---

def test_markdown_renderer_for_pr_comments():
    """Test markdown renderer produces GitHub-compatible output."""

    # Arrange
    results = create_test_results(
        overall_status="fail",
        violations=[
            {"rule": "missing_check", "severity": "error", "message": "Too many missing values"},
            {"rule": "type_check", "severity": "warn", "message": "Incorrect data type"}
        ],
        terminated_early=True,
        termination_rule="critical_rule"
    )

    # Act
    renderer = ReportRenderer("markdown")
    markdown = renderer.render_report(results)

    # Assert
    assert "## Dataset Audit Report" in markdown
    assert "| Status |" in markdown  # Check for table structure
    assert "<details>" in markdown  # Check for collapsible GitHub section
    assert "⚠️ Audit stopped early" in markdown or "terminated early" in markdown.lower()
    assert len(markdown) < 65536  # GitHub comment max size safety
