import pytest
from echidna_agent.agents.fix_agent import FixSuggestion

def test_fix_models():
    fix = FixSuggestion(
        original_code="code",
        fixed_code="fixed",
        explanation="exp",
        diff="diff"
    )
    assert fix.original_code == "code"
