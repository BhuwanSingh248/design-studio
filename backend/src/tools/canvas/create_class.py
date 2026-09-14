from src.tools.base import BaseTool, ToolContext, ToolResult
from src.tools.schemas import CreateClassInput


class CreateClassTool(BaseTool):
    name = "create_class"
    description = "Create a new class on the design canvas."
    input_schema = CreateClassInput

    async def execute(self, params: CreateClassInput, context: ToolContext) -> ToolResult:
        return ToolResult(
            success=True,
            data={
                "operation": "create_class",
                "class_name": params.name,
                "workspace_id": context.workspace_id,
                "canvas_id": context.canvas_id,
            },
        )
