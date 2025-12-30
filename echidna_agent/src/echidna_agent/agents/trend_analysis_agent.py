from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, TypedDict
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from ..config import settings
from ..db import get_db_connection
import json

class TrendDashboard(BaseModel):
    total_audits: int = Field(description="Total number of audits/triage jobs analyzed")
    vulnerability_counts: Dict[str, int] = Field(description="Count of vulnerabilities by category")
    top_vulnerabilities: List[str] = Field(description="List of most frequent vulnerability categories")
    analysis_summary: str = Field(description="AI analysis of the trends")

class TrendInput(BaseModel):
    time_range_days: int = Field(default=30, description="Number of days to analyze")

class TrendState(TypedDict):
    time_range_days: int
    raw_data: Optional[List[Dict[str, Any]]]
    result: Optional[TrendDashboard]

async def fetch_data(state: TrendState):
    # Query agent_jobs for triage_agent outputs
    async with await get_db_connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                SELECT output_payload 
                FROM echidna_agents.agent_jobs 
                WHERE agent_name = 'triage_agent' 
                AND status = 'completed'
                AND created_at > NOW() - INTERVAL '%s days'
                """,
                (state["time_range_days"],)
            )
            rows = await cur.fetchall()
            
    data = []
    for row in rows:
        if row[0]:
            # row[0] is dict (jsonb)
            data.append(row[0])
            
    return {"raw_data": data}

def analyze_trends(state: TrendState):
    model = ChatOpenAI(model=settings.AGENT_MODEL_DEFAULT, api_key=settings.OPENAI_API_KEY)
    parser = PydanticOutputParser(pydantic_object=TrendDashboard)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a security data analyst. Analyze the audit findings and generate a trend dashboard. \\n{format_instructions}"),
        ("user", "Audit Data:\\n{raw_data}")
    ])
    
    chain = prompt | model | parser
    
    result = chain.invoke({
        "raw_data": json.dumps(state["raw_data"]),
        "format_instructions": parser.get_format_instructions()
    })
    
    return {"result": result}

workflow = StateGraph(TrendState)
workflow.add_node("fetch", fetch_data)
workflow.add_node("analyze", analyze_trends)
workflow.set_entry_point("fetch")
workflow.add_edge("fetch", "analyze")
workflow.add_edge("analyze", END)

trend_agent_runnable = workflow.compile()
