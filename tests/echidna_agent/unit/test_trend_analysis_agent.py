import pytest
from echidna_agent.agents.trend_analysis_agent import TrendDashboard

def test_trend_models():
    dashboard = TrendDashboard(
        total_audits=10,
        vulnerability_counts={"High": 5},
        top_vulnerabilities=["Reentrancy"],
        analysis_summary="Summary"
    )
    assert dashboard.total_audits == 10
