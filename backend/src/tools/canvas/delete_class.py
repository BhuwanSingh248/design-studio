from src.tools.base import BaseTool, ToolContext, ToolResult
from src.tools.schemas import DeleteClassInput


class DeleteClassTool(BaseTool):
    name = "delete_class"
    description = "Delete an existing class from the design canvas by its ID."
    input_schema = DeleteClassInput

    async def execute(self, params: DeleteClassInput, context: ToolContext) -> ToolResult:
        return ToolResult(
            success=True,
            data={
                "operation": "delete_class",
                "class_id": params.class_id,
                "workspace_id": context.workspace_id,
                "canvas_id": context.canvas_id,
            },
        )
