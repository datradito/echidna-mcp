import pytest
from echidna_agent.agents.report_summarizer import AuditReport, AuditFinding

def test_report_models():
    finding = AuditFinding(
        id="1", title="T", description="D", severity="High", category="C"
    )
    report = AuditReport(
        title="Report",
        executive_summary="Exec",
        technical_details="Tech",
        risk_assessment="Risk",
        recommendations="Rec"
    )
    assert report.title == "Report"
