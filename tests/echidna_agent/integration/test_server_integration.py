import pytest
import asyncio
import json
from echidna_agent.server import agent_triage_issue, check_agent_job_status

@pytest.mark.asyncio
async def test_triage_flow():
    # Call the tool
    job_id_str = await agent_triage_issue(
        failure_log="Error: Reentrancy in Contract.sol",
        contract_code="contract C { function f() { call(); } }"
    )
    assert job_id_str
    
    # Check status immediately
    status_json = await check_agent_job_status(job_id_str)
    status_data = json.loads(status_json)
    assert status_data["job_id"] == job_id_str
    assert status_data["status"] in ["queued", "running", "completed", "failed"]
    
    # Allow background task to start
    await asyncio.sleep(1)
    
    # Check status again
    status_json = await check_agent_job_status(job_id_str)
    status_data = json.loads(status_json)
    print(f"Job status: {status_data['status']}")
    if status_data["status"] == "failed":
        print(f"Error: {status_data.get('error_message')}")
