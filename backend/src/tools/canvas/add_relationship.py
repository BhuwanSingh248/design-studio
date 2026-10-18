from src.domain.repositories.canvas_repository import CanvasRepository
from src.domain.services.canvas_service import CanvasService
from src.tools.base import BaseTool, ToolContext, ToolResult
from src.tools.schemas import AddRelationshipInput


class AddRelationshipTool(BaseTool):
    name = "add_relationship"
    description = "Add a relationship between two classes on the canvas."
    input_schema = AddRelationshipInput

    def __init__(
        self,
        canvas_service: CanvasService,
        canvas_repository: CanvasRepository,
    ):
        self.canvas_service = canvas_service
        self.canvas_repository = canvas_repository

    async def execute(
        self, params: AddRelationshipInput, context: ToolContext
    ) -> ToolResult:
        canvas = await self.canvas_repository.get(
            context.workspace_id, context.canvas_id
        )
        relationship = self.canvas_service.add_relationship(
            canvas,
            params.source_id,
            params.target_id,
            params.relationship_type,
        )
        await self.canvas_repository.save(
            context.workspace_id, context.canvas_id, canvas
        )
        return ToolResult(
            success=True,
            data={
                "operation": "add_relationship",
                "relationship_id": relationship.id,
                "source_id": relationship.source_id,
                "target_id": relationship.target_id,
                "relationship_type": relationship.relation_type.value,
                "workspace_id": context.workspace_id,
                "canvas_id": context.canvas_id,
            },
        )
