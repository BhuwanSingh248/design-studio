from src.tools.base import BaseTool, ToolContext, ToolResult
from src.tools.schemas import AddAttributeInput


class AddAttributeTool(BaseTool):
    name = "add_attribute"
    description = "Add an attribute/field to a class on the canvas."
    input_schema = AddAttributeInput

    async def execute(self, params: AddAttributeInput, context: ToolContext) -> ToolResult:
        return ToolResult(
            success=True,
            data={
                "operation": "add_attribute",
                "class_id": params.class_id,
                "attribute_name": params.name,
                "attribute_type": params.type,
                "default": params.default,
                "workspace_id": context.workspace_id,
                "canvas_id": context.canvas_id,
            },
        )
