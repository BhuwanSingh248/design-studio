import asyncio
from src.tools.base import ToolContext
from src.tools.harness import ToolExecutionHarness
from src.tools.registry import ToolRegistry


def test_tool_harness_loop():
    registry = ToolRegistry()
    harness = ToolExecutionHarness(registry=registry)
    ctx = ToolContext(workspace_id="w1", canvas_id="c1")
    result = asyncio.run(harness.run_loop("Create User class", ctx))
    assert result["result"] == "completed"

