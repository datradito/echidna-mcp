from pydantic import BaseModel, Field
from typing import Any, Dict, Optional, Literal
from uuid import UUID, uuid4
from datetime import datetime
import asyncio
import json
from ..db import get_db_connection
from ..config import settings

class AgentJob(BaseModel):
    job_id: UUID = Field(default_factory=uuid4)
    agent_name: str
    status: Literal['queued', 'running', 'completed', 'failed'] = 'queued'
    input_payload: Dict[str, Any]
    output_payload: Optional[Dict[str, Any]] = None
    error_message: Optional[Dict[str, Any]] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

async def create_job(agent_name: str, input_payload: Dict[str, Any]) -> UUID:
    job_id = uuid4()
    async with await get_db_connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                INSERT INTO echidna_agents.agent_jobs 
                (job_id, agent_name, status, input_payload, created_at, updated_at)
                VALUES (%s, %s, 'queued', %s, NOW(), NOW())
                """,
                (job_id, agent_name, json.dumps(input_payload))
            )
            await conn.commit()
    return job_id

async def update_job_status(
    job_id: UUID, 
    status: str, 
    output_payload: Optional[Dict[str, Any]] = None, 
    error_message: Optional[Dict[str, Any]] = None
):
    async with await get_db_connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                UPDATE echidna_agents.agent_jobs 
                SET status = %s, 
                    output_payload = %s, 
                    error_message = %s, 
                    updated_at = NOW()
                WHERE job_id = %s
                """,
                (
                    status, 
                    json.dumps(output_payload) if output_payload else None, 
                    json.dumps(error_message) if error_message else None, 
                    job_id
                )
            )
            await conn.commit()

async def get_job(job_id: UUID) -> Optional[AgentJob]:
    async with await get_db_connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                SELECT job_id, agent_name, status, input_payload, output_payload, error_message, created_at, updated_at
                FROM echidna_agents.agent_jobs
                WHERE job_id = %s
                """,
                (job_id,)
            )
            row = await cur.fetchone()
            if row:
                return AgentJob(
                    job_id=row[0],
                    agent_name=row[1],
                    status=row[2],
                    input_payload=row[3],
                    output_payload=row[4],
                    error_message=row[5],
                    created_at=row[6],
                    updated_at=row[7]
                )
    return None

async def run_agent_task(job_id: UUID, agent_runnable, input_data: Dict[str, Any]):
    """
    Background task to run the agent and update job status.
    """
    try:
        await update_job_status(job_id, 'running')
        
        # Run the agent
        # Assuming agent_runnable is a LangChain/LangGraph runnable
        result = await agent_runnable.ainvoke(input_data)
        
        await update_job_status(job_id, 'completed', output_payload=result)
    except Exception as e:
        error_info = {"error": str(e), "type": type(e).__name__}
        await update_job_status(job_id, 'failed', error_message=error_info)
