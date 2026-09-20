from src.tools.base import BaseTool, ToolContext, ToolResult
from src.tools.schemas import CreateClassInput
from src.domain.services.canvas_service import CanvasService
from src.domain.repositoriers.canvas_repository import CanvasRepository


class CreateClassTool(BaseTool):
    name = "create_class"
    description = "Create a new class on the design canvas."
    input_schema = CreateClassInput

    def __init__(self, canvas_service:CanvasService, canvas_repository:CanvasRepository):
        self.canvas_service=canvas_service
        self.canvas_repository=canvas_repository

    async def execute(
        self, 
        params: CreateClassInput, 
        context: ToolContext
    ) -> ToolResult:
        # obtain the CanvasState for context.canvas_id
        canvas=await self.canvas_repository.get(context.canvas_id)

        # call canvas_service.create_class(...)
        created_class = self.canvas_service.create_class(canvas, params.name)
        
        # convert returned ClassDefinition into ToolResult
        return ToolResult(
            success=True,
            data={
                "operation": "create_class",
                "class_name": created_class.name,
                "class_id": created_class.id,
                "workspace_id": context.workspace_id,
                "canvas_id": context.canvas_id,
            },
        )
