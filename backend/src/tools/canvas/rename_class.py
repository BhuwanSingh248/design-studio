from src.tools.base import BaseTool, ToolContext, ToolResult
from src.tools.schemas import RenameClassInput


class RenameClassTool(BaseTool):
    name = "rename_class"
    description = "Rename an existing class on the design canvas."
    input_schema = RenameClassInput

    async def execute(self, params: RenameClassInput, context: ToolContext) -> ToolResult:
        return ToolResult(
            success=True,
            data={
                "operation": "rename_class",
                "class_id": params.class_id,
                "new_name": params.new_name,
                "workspace_id": context.workspace_id,
                "canvas_id": context.canvas_id,
            },
        )
