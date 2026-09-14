from src.tools.base import BaseTool, ToolContext, ToolResult
from src.tools.schemas import AddMethodInput


class AddMethodTool(BaseTool):
    name = "add_method"
    description = "Add a method/behavior to a class on the canvas."
    input_schema = AddMethodInput

    async def execute(self, params: AddMethodInput, context: ToolContext) -> ToolResult:
        return ToolResult(
            success=True,
            data={
                "operation": "add_method",
                "class_id": params.class_id,
                "method_name": params.name,
                "return_type": params.return_type,
                "parameters": params.parameters,
                "workspace_id": context.workspace_id,
                "canvas_id": context.canvas_id,
            },
        )
