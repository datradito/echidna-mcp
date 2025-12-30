from pydantic import BaseModel, Field
from typing import List, Optional, Literal, TypedDict
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from ..config import settings
from .triage_agent import AuditFinding

class AuditReport(BaseModel):
    title: str = Field(description="Title of the audit report")
    executive_summary: str = Field(description="High-level summary for stakeholders")
    technical_details: str = Field(description="Detailed technical analysis of findings")
    risk_assessment: str = Field(description="Assessment of overall risk posture")
    recommendations: str = Field(description="Consolidated recommendations")

class ReportInput(BaseModel):
    findings: List[AuditFinding] = Field(description="List of findings to summarize")
    verbosity: Literal["brief", "technical", "executive"] = Field(description="Desired verbosity level")

class ReportState(TypedDict):
    findings: List[AuditFinding]
    verbosity: str
    result: Optional[AuditReport]

def summarize_report(state: ReportState):
    model = ChatOpenAI(model=settings.AGENT_MODEL_DEFAULT, api_key=settings.OPENAI_API_KEY)
    parser = PydanticOutputParser(pydantic_object=AuditReport)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert security auditor. Generate an audit report based on the findings. Verbosity: {verbosity}. \\n{format_instructions}"),
        ("user", "Findings:\\n{findings}")
    ])
    
    # Serialize findings
    findings_json = [f.model_dump() for f in state["findings"]]
    
    chain = prompt | model | parser
    
    result = chain.invoke({
        "findings": findings_json,
        "verbosity": state["verbosity"],
        "format_instructions": parser.get_format_instructions()
    })
    
    return {"result": result}

workflow = StateGraph(ReportState)
workflow.add_node("summarize", summarize_report)
workflow.set_entry_point("summarize")
workflow.add_edge("summarize", END)

report_summarizer_runnable = workflow.compile()
