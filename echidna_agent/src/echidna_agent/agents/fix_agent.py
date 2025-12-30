from pydantic import BaseModel, Field
from typing import Optional, TypedDict
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from ..config import settings

class FixSuggestion(BaseModel):
    original_code: str = Field(description="The original vulnerable code snippet")
    fixed_code: str = Field(description="The suggested fixed code")
    explanation: str = Field(description="Explanation of why this fix works")
    diff: str = Field(description="Unified diff of the changes")

class FixInput(BaseModel):
    contract_code: str = Field(description="Source code of the contract")
    vulnerability_description: str = Field(description="Description of the vulnerability to fix")
    line_number: Optional[int] = Field(default=None, description="Line number of the issue")

class FixState(TypedDict):
    contract_code: str
    vulnerability_description: str
    line_number: Optional[int]
    result: Optional[FixSuggestion]

def suggest_fix(state: FixState):
    model = ChatOpenAI(model=settings.AGENT_MODEL_FIX, api_key=settings.OPENAI_API_KEY)
    parser = PydanticOutputParser(pydantic_object=FixSuggestion)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert smart contract developer. Suggest a fix for the described vulnerability. \\n{format_instructions}"),
        ("user", "Contract Code:\\n{contract_code}\\n\\nVulnerability:\\n{vulnerability_description}\\nLine: {line_number}")
    ])
    
    chain = prompt | model | parser
    
    result = chain.invoke({
        "contract_code": state["contract_code"],
        "vulnerability_description": state["vulnerability_description"],
        "line_number": state.get("line_number", "Unknown"),
        "format_instructions": parser.get_format_instructions()
    })
    
    return {"result": result}

workflow = StateGraph(FixState)
workflow.add_node("fix", suggest_fix)
workflow.set_entry_point("fix")
workflow.add_edge("fix", END)

fix_agent_runnable = workflow.compile()
