from mcp.server.fastmcp import FastMCP
from uuid import UUID
from .agents.base import get_job, create_job, run_agent_task
from .agents.triage_agent import triage_agent_runnable
from .agents.fuzzer_opt_agent import fuzzer_opt_agent_runnable, FuzzMetrics
from .agents.report_summarizer import report_summarizer_runnable, AuditFinding
from .agents.fix_agent import fix_agent_runnable
from .agents.trend_analysis_agent import trend_agent_runnable
import json
import asyncio

# Initialize FastMCP server
mcp = FastMCP("Echidna Agent")

@mcp.tool()
async def check_agent_job_status(job_id: str) -> str:
    """
    Check the status of an agent job.
    
    Args:
        job_id: The UUID of the job to check.
    """
    try:
        uuid_obj = UUID(job_id)
    except ValueError:
        return f"Invalid UUID format: {job_id}"
        
    job = await get_job(uuid_obj)
    if not job:
        return f"Job {job_id} not found."
    
    # Return formatted JSON string of the job details
    return json.dumps(job.model_dump(mode='json'), indent=2)

@mcp.tool()
async def agent_triage_issue(failure_log: str, contract_code: str = None) -> str:
    """
    Analyze an Echidna failure log to classify the issue severity and type.
    
    Args:
        failure_log: The raw failure log output from Echidna.
        contract_code: Optional source code of the contract related to the failure.
        
    Returns:
        A Job ID (UUID) to track the analysis progress.
    """
    input_data = {"failure_log": failure_log, "contract_code": contract_code}
    
    # Create job
    job_id = await create_job("triage_agent", input_data)
    
    # Start background task
    asyncio.create_task(run_agent_task(job_id, triage_agent_runnable, input_data))
    
    return str(job_id)

@mcp.tool()
async def agent_optimize_fuzzer(metrics: dict, current_config: dict = None) -> str:
    """
    Analyze fuzzing metrics and suggest optimization parameters.
    
    Args:
        metrics: Dictionary containing fuzzing metrics (coverage_percentage, runtime_seconds, crashes_found, unique_paths, corpus_size).
        current_config: Optional dictionary of the current Echidna configuration.
        
    Returns:
        A Job ID (UUID) to track the optimization progress.
    """
    try:
        metrics_obj = FuzzMetrics(**metrics)
    except Exception as e:
        return f"Invalid metrics: {e}"
        
    # Prepare input for the agent (needs Pydantic object)
    agent_input = {"metrics": metrics_obj, "current_config": current_config}
    
    # Prepare input for DB (needs JSON serializable dict)
    db_input = {"metrics": metrics, "current_config": current_config}
    
    # Create job
    job_id = await create_job("fuzzer_opt_agent", db_input)
    
    # Start background task
    asyncio.create_task(run_agent_task(job_id, fuzzer_opt_agent_runnable, agent_input))
    
    return str(job_id)

@mcp.tool()
async def agent_summarize_report(findings: list, verbosity: str = "technical") -> str:
    """
    Generate an audit report summary from a list of findings.
    
    Args:
        findings: List of finding objects (dictionaries).
        verbosity: Desired verbosity level ("brief", "technical", "executive").
        
    Returns:
        A Job ID (UUID) to track the report generation.
    """
    try:
        findings_objs = [AuditFinding(**f) for f in findings]
    except Exception as e:
        return f"Invalid findings: {e}"
        
    agent_input = {"findings": findings_objs, "verbosity": verbosity}
    db_input = {"findings": findings, "verbosity": verbosity}
    
    job_id = await create_job("report_summarizer", db_input)
    
    asyncio.create_task(run_agent_task(job_id, report_summarizer_runnable, agent_input))
    
    return str(job_id)

@mcp.tool()
async def agent_suggest_fix(contract_code: str, vulnerability_description: str, line_number: int = None) -> str:
    """
    Suggest a fix for a smart contract vulnerability.
    
    Args:
        contract_code: The source code of the contract.
        vulnerability_description: Description of the vulnerability.
        line_number: Optional line number where the issue is located.
        
    Returns:
        A Job ID (UUID) to track the fix suggestion.
    """
    input_data = {
        "contract_code": contract_code,
        "vulnerability_description": vulnerability_description,
        "line_number": line_number
    }
    
    job_id = await create_job("fix_agent", input_data)
    
    asyncio.create_task(run_agent_task(job_id, fix_agent_runnable, input_data))
    
    return str(job_id)

@mcp.tool()
async def agent_analyze_trends(time_range_days: int = 30) -> str:
    """
    Analyze audit trends from historical data.
    
    Args:
        time_range_days: Number of days to look back for analysis.
        
    Returns:
        A Job ID (UUID) to track the analysis.
    """
    input_data = {"time_range_days": time_range_days}
    
    job_id = await create_job("trend_analysis_agent", input_data)
    
    asyncio.create_task(run_agent_task(job_id, trend_agent_runnable, input_data))
    
    return str(job_id)

if __name__ == "__main__":
    mcp.run()
