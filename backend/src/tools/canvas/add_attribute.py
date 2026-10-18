from src.domain.repositories.canvas_repository import CanvasRepository
from src.domain.services.canvas_service import CanvasService
from src.tools.base import BaseTool, ToolContext, ToolResult
from src.tools.schemas import AddAttributeInput


class AddAttributeTool(BaseTool):
    name = "add_attribute"
    description = "Add an attribute/field to a class on the canvas."
    input_schema = AddAttributeInput

    def __init__(
        self,
        canvas_service: CanvasService,
        canvas_repository: CanvasRepository,
    ):
        self.canvas_service = canvas_service
        self.canvas_repository = canvas_repository

    async def execute(
        self, params: AddAttributeInput, context: ToolContext
    ) -> ToolResult:
        canvas = await self.canvas_repository.get(
            context.workspace_id, context.canvas_id
        )
        attribute = self.canvas_service.add_attribute(
            canvas,
            params.class_id,
            params.name,
            params.type,
            params.default,
        )
        await self.canvas_repository.save(
            context.workspace_id, context.canvas_id, canvas
        )
        return ToolResult(
            success=True,
            data={
                "operation": "add_attribute",
                "class_id": params.class_id,
                "attribute_name": attribute.name,
                "attribute_type": attribute.data_type,
                "default": attribute.default,
                "workspace_id": context.workspace_id,
                "canvas_id": context.canvas_id,
            },
        )
