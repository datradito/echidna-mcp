from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Dict, Any, TypedDict
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from ..config import settings
from .base import AgentJob

class AuditFinding(BaseModel):
    id: str = Field(description="Unique identifier for the finding")
    title: str = Field(description="Short title of the finding")
    description: str = Field(description="Detailed description of the finding")
    severity: Literal["High", "Medium", "Low", "Informational"] = Field(description="Severity level")
    category: str = Field(description="Category of the vulnerability (e.g., Reentrancy, Logic Error)")
    location: Optional[str] = Field(default=None, description="File path and line number if available")
    reproduction_steps: Optional[str] = Field(default=None, description="Steps to reproduce the issue")

class TriageResult(BaseModel):
    findings: List[AuditFinding] = Field(description="List of findings identified")
    summary: str = Field(description="Summary of the triage analysis")

class TriageInput(BaseModel):
    failure_log: str = Field(description="Raw failure log from Echidna")
    contract_code: Optional[str] = Field(description="Source code of the contract (optional but recommended)")

class TriageState(TypedDict):
    failure_log: str
    contract_code: Optional[str]
    result: Optional[TriageResult]

def analyze_failure(state: TriageState):
    model = ChatOpenAI(model=settings.AGENT_MODEL_TRIAGE, api_key=settings.OPENAI_API_KEY)
    parser = PydanticOutputParser(pydantic_object=TriageResult)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert smart contract auditor. Analyze the following Echidna failure log and classify the issue. \\n{format_instructions}"),
        ("user", "Failure Log:\\n{failure_log}\\n\\nContract Code:\\n{contract_code}")
    ])
    
    chain = prompt | model | parser
    
    result = chain.invoke({
        "failure_log": state["failure_log"],
        "contract_code": state.get("contract_code", "Not provided"),
        "format_instructions": parser.get_format_instructions()
    })
    
    return {"result": result}

workflow = StateGraph(TriageState)
workflow.add_node("analyze", analyze_failure)
workflow.set_entry_point("analyze")
workflow.add_edge("analyze", END)

triage_agent_runnable = workflow.compile()
