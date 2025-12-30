import pytest
from unittest.mock import MagicMock, patch
from echidna_agent.agents.triage_agent import TriageResult, AuditFinding

def test_triage_models():
    finding = AuditFinding(
        id="1", 
        title="Reentrancy", 
        description="A reentrancy vulnerability.", 
        severity="High", 
        category="Reentrancy",
        location="src/Contract.sol:10",
        reproduction_steps="Call attack()"
    )
    result = TriageResult(findings=[finding], summary="Found 1 issue.")
    assert len(result.findings) == 1
    assert result.findings[0].severity == "High"
    assert result.findings[0].category == "Reentrancy"
