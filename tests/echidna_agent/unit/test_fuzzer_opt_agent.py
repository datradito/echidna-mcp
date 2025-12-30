import pytest
from echidna_agent.agents.fuzzer_opt_agent import FuzzMetrics, OptimizationPlan

def test_fuzzer_opt_models():
    metrics = FuzzMetrics(
        coverage_percentage=50.5,
        runtime_seconds=3600,
        crashes_found=2,
        unique_paths=100,
        corpus_size=50
    )
    assert metrics.coverage_percentage == 50.5
    
    plan = OptimizationPlan(
        suggested_mutators=["M1", "M2"],
        seed_strategy="Use corpus",
        config_adjustments={"timeout": 7200},
        reasoning="Increase timeout"
    )
    assert len(plan.suggested_mutators) == 2
