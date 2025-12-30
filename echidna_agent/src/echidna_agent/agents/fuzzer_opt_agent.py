from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, TypedDict
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from ..config import settings

class FuzzMetrics(BaseModel):
    coverage_percentage: float = Field(description="Code coverage percentage achieved")
    runtime_seconds: float = Field(description="Duration of the fuzzing run in seconds")
    crashes_found: int = Field(description="Number of crashes/failures found")
    unique_paths: int = Field(description="Number of unique paths explored")
    corpus_size: int = Field(description="Size of the generated corpus")

class OptimizationPlan(BaseModel):
    suggested_mutators: List[str] = Field(description="List of mutators to enable/prioritize")
    seed_strategy: str = Field(description="Strategy for seed selection/generation")
    config_adjustments: Dict[str, Any] = Field(description="Recommended configuration changes")
    reasoning: str = Field(description="Explanation for the suggestions")

class FuzzerOptInput(BaseModel):
    metrics: FuzzMetrics
    current_config: Optional[Dict[str, Any]] = Field(description="Current Echidna configuration")

class FuzzerOptState(TypedDict):
    metrics: FuzzMetrics
    current_config: Optional[Dict[str, Any]]
    result: Optional[OptimizationPlan]

def optimize_fuzzer(state: FuzzerOptState):
    model = ChatOpenAI(model=settings.AGENT_MODEL_DEFAULT, api_key=settings.OPENAI_API_KEY)
    parser = PydanticOutputParser(pydantic_object=OptimizationPlan)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert in fuzzing and Echidna configuration. Analyze the metrics and suggest optimizations. \\n{format_instructions}"),
        ("user", "Metrics:\\n{metrics}\\n\\nCurrent Config:\\n{current_config}")
    ])
    
    chain = prompt | model | parser
    
    result = chain.invoke({
        "metrics": state["metrics"].model_dump_json(),
        "current_config": state.get("current_config", {}),
        "format_instructions": parser.get_format_instructions()
    })
    
    return {"result": result}

workflow = StateGraph(FuzzerOptState)
workflow.add_node("optimize", optimize_fuzzer)
workflow.set_entry_point("optimize")
workflow.add_edge("optimize", END)

fuzzer_opt_agent_runnable = workflow.compile()
