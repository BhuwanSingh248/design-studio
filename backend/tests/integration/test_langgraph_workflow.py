"""Integration tests for LangGraph state machine."""
from src.agents.graph import DesignWorkflowGraph


def test_workflow_graph_instantiation():
    graph = DesignWorkflowGraph()
    assert graph is not None
