from src.domain.repositories.canvas_repository import CanvasRepository
from src.domain.services.canvas_service import CanvasService
from src.tools.base import BaseTool, ToolContext, ToolResult
from src.tools.schemas import RemoveAttributeInput


class RemoveAttributeTool(BaseTool):
    name = "remove_attribute"
    description = "Remove an attribute/field from a class on the canvas."
    input_schema = RemoveAttributeInput

    def __init__(
        self,
        canvas_service: CanvasService,
        canvas_repository: CanvasRepository,
    ):
        self.canvas_service = canvas_service
        self.canvas_repository = canvas_repository

    async def execute(
        self, params: RemoveAttributeInput, context: ToolContext
    ) -> ToolResult:
        canvas = await self.canvas_repository.get(
            context.workspace_id, context.canvas_id
        )
        attribute = self.canvas_service.remove_attribute(
            canvas, params.class_id, params.name
        )
        await self.canvas_repository.save(
            context.workspace_id, context.canvas_id, canvas
        )
        return ToolResult(
            success=True,
            data={
                "operation": "remove_attribute",
                "class_id": params.class_id,
                "attribute_name": attribute.name,
                "attribute_type": attribute.data_type,
                "workspace_id": context.workspace_id,
                "canvas_id": context.canvas_id,
            },
        )
