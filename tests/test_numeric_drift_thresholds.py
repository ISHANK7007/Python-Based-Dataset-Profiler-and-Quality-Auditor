import os
import json
from profiler.dataset_profile import DatasetProfile
from drift.drift_auditor import analyze_dataset_drift

def send_alert(subject: str, payload: dict):
    """
    Temporary alert mockup function. Prints alert info to console.
    """
    print(f"[ALERT] {subject}")
    for item in payload:
        print(f" - {item}")

def save_drift_reports(report, base_path, baseline_name, current_name):
    """
    Generate and save drift report in Markdown, JSON, Excel, and HTML formats.
    """
    if not os.path.exists(base_path):
        os.makedirs(base_path)

    report_name = f"drift_report_{baseline_name}_to_{current_name}"
    timestamp = report.timestamp.strftime("%Y%m%d_%H%M%S")

    # Save Markdown report
    md_report = report.to_markdown()
    with open(os.path.join(base_path, f"{report_name}_{timestamp}.md"), "w", encoding="utf-8") as f:
        f.write(md_report)

    # Save JSON report
    json_report = report.to_json()
    with open(os.path.join(base_path, f"{report_name}_{timestamp}.json"), "w", encoding="utf-8") as f:
        f.write(json_report)

    # Save Excel report
    report.to_excel(os.path.join(base_path, f"{report_name}_{timestamp}.xlsx"))

    # Save HTML report
    html_report = report.to_html()
    with open(os.path.join(base_path, f"{report_name}_{timestamp}.html"), "w", encoding="utf-8") as f:
        f.write(html_report)

    print(f"✔ Reports saved to {base_path}/{report_name}_{timestamp}.*")

# === Example Analysis Pipeline ===

if __name__ == "__main__":
    baseline_profile = DatasetProfile.load("sales_data_2022Q1.json")
    current_profile = DatasetProfile.load("sales_data_2022Q2.json")

    # Analyze drift
    report = analyze_dataset_drift(baseline_profile, current_profile)

    # Save all report formats
    save_drift_reports(report, base_path="./reports", baseline_name="2022Q1", current_name="2022Q2")

    # Extract major issues for alerting
    major_findings = report.filter_findings(severity="major")
    if major_findings:
        send_alert("🚨 Major data drift detected", major_findings)
