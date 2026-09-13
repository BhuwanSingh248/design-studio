"""LangGraph AgentState TypedDict."""
from typing import Any, TypedDict


class AgentState(TypedDict):
    canvas_id: str
    query: str
    issues: list[dict]
    recommendations: list[dict]
    plan: list[dict]
    approved: bool
    tool_results: list[Any]
