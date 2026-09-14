from src.tools.base import BaseTool, ToolContext, ToolResult
from src.tools.schemas import RemoveRelationshipInput


class RemoveRelationshipTool(BaseTool):
    name = "remove_relationship"
    description = "Remove a relationship between two classes on the canvas."
    input_schema = RemoveRelationshipInput

    async def execute(self, params: RemoveRelationshipInput, context: ToolContext) -> ToolResult:
        return ToolResult(
            success=True,
            data={
                "operation": "remove_relationship",
                "source_id": params.source_id,
                "target_id": params.target_id,
                "relationship_type": params.relationship_type.value,
                "workspace_id": context.workspace_id,
                "canvas_id": context.canvas_id,
            },
        )
