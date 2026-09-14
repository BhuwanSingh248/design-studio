from src.tools.base import BaseTool, ToolContext, ToolResult
from src.tools.schemas import RemoveAttributeInput


class RemoveAttributeTool(BaseTool):
    name = "remove_attribute"
    description = "Remove an attribute/field from a class on the canvas."
    input_schema = RemoveAttributeInput

    async def execute(self, params: RemoveAttributeInput, context: ToolContext) -> ToolResult:
        return ToolResult(
            success=True,
            data={
                "operation": "remove_attribute",
                "class_id": params.class_id,
                "attribute_name": params.name,
                "workspace_id": context.workspace_id,
                "canvas_id": context.canvas_id,
            },
        )
