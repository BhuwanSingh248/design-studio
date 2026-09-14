from src.tools.base import BaseTool, ToolContext, ToolResult
from src.tools.schemas import AddRelationshipInput


class AddRelationshipTool(BaseTool):
    name = "add_relationship"
    description = "Add a relationship between two classes on the canvas."
    input_schema = AddRelationshipInput

    async def execute(self, params: AddRelationshipInput, context: ToolContext) -> ToolResult:
        return ToolResult(
            success=True,
            data={
                "operation": "add_relationship",
                "source_id": params.source_id,
                "target_id": params.target_id,
                "relationship_type": params.relationship_type.value,
                "workspace_id": context.workspace_id,
                "canvas_id": context.canvas_id,
            },
        )
