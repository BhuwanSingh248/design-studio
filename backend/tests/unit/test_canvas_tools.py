import asyncio
from src.tools.base import ToolContext
from src.tools.canvas_tools import CreateClassParams, CreateClassTool


def test_create_class_tool():
    tool = CreateClassTool()
    ctx = ToolContext(workspace_id="w1", canvas_id="can1")
    params = CreateClassParams(name="Order")
    result = asyncio.run(tool.execute(params, ctx))
    assert result.success is True
    assert result.data["class_created"] == "Order"

