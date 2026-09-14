from src.tools.base import BaseTool, ToolContext, ToolResult
from src.tools.schemas import RemoveMethodInput


class RemoveMethodTool(BaseTool):
    name = "remove_method"
    description = "Remove a method from a class on the canvas."
    input_schema = RemoveMethodInput

    async def execute(self, params: RemoveMethodInput, context: ToolContext) -> ToolResult:
        return ToolResult(
            success=True,
            data={
                "operation": "remove_method",
                "class_id": params.class_id,
                "method_name": params.name,
                "workspace_id": context.workspace_id,
                "canvas_id": context.canvas_id,
            },
        )
