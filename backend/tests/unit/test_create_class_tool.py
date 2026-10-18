"""Focused tests for CreateClassTool and its repository/service boundary."""

import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest
from src.domain.models.canvas import CanvasState, ClassDefinition
from src.domain.repositories.canvas_repository import CanvasRepository
from src.domain.services.canvas_service import CanvasService
from src.tools.base import ToolContext
from src.tools.canvas.create_class import CreateClassTool
from src.tools.registry import ToolRegistry
from src.tools.schemas import CreateClassInput


@pytest.fixture
def tool_context() -> ToolContext:
    return ToolContext(workspace_id="ws-123", canvas_id="canvas-456")


@pytest.fixture
def canvas_service() -> CanvasService:
    return CanvasService()


@pytest.fixture
def canvas_repository(tool_context: ToolContext) -> CanvasRepository:
    repository = CanvasRepository()
    asyncio.run(
        repository.save(
            tool_context.workspace_id,
            tool_context.canvas_id,
            CanvasState(),
        )
    )
    return repository


@pytest.fixture
def create_class_tool(canvas_service, canvas_repository) -> CreateClassTool:
    return CreateClassTool(
        canvas_service=canvas_service,
        canvas_repository=canvas_repository,
    )


def test_create_class_tool_metadata(create_class_tool):
    assert create_class_tool.name == "create_class"
    assert create_class_tool.input_schema is CreateClassInput


def test_execute_success(create_class_tool, canvas_repository, tool_context):
    result = asyncio.run(
        create_class_tool.execute(CreateClassInput(name="Order"), tool_context)
    )
    canvas = asyncio.run(
        canvas_repository.get(tool_context.workspace_id, tool_context.canvas_id)
    )

    assert result.success is True
    assert result.error is None
    assert result.data["operation"] == "create_class"
    assert result.data["class_name"] == "Order"
    assert result.data["workspace_id"] == tool_context.workspace_id
    assert result.data["canvas_id"] == tool_context.canvas_id
    assert len(canvas.classes) == 1
    assert canvas.classes[0].id == result.data["class_id"]


def test_execute_duplicate_class_raises_value_error(create_class_tool, tool_context):
    asyncio.run(
        create_class_tool.execute(CreateClassInput(name="Product"), tool_context)
    )

    with pytest.raises(ValueError, match="already exists"):
        asyncio.run(
            create_class_tool.execute(CreateClassInput(name="Product"), tool_context)
        )


def test_execute_missing_canvas_raises_value_error(create_class_tool):
    missing_context = ToolContext(workspace_id="ws-123", canvas_id="missing")
    with pytest.raises(ValueError, match="not found"):
        asyncio.run(
            create_class_tool.execute(CreateClassInput(name="Account"), missing_context)
        )


def test_execute_with_mocked_dependencies(tool_context):
    mock_repository = AsyncMock(spec=CanvasRepository)
    mock_service = MagicMock(spec=CanvasService)
    fake_canvas = CanvasState()
    mock_repository.get.return_value = fake_canvas
    mock_service.create_class.return_value = ClassDefinition(
        id="fake-id",
        name="Payment",
    )
    tool = CreateClassTool(
        canvas_service=mock_service,
        canvas_repository=mock_repository,
    )

    result = asyncio.run(
        tool.execute(CreateClassInput(name="Payment"), tool_context)
    )

    mock_repository.get.assert_awaited_once_with(
        tool_context.workspace_id,
        tool_context.canvas_id,
    )
    mock_service.create_class.assert_called_once_with(fake_canvas, "Payment")
    mock_repository.save.assert_awaited_once_with(
        tool_context.workspace_id,
        tool_context.canvas_id,
        fake_canvas,
    )
    assert result.success is True
    assert result.data["class_id"] == "fake-id"


def test_registry_dispatch_and_validation(create_class_tool, tool_context):
    registry = ToolRegistry()
    registry.register_tool(create_class_tool)

    result = asyncio.run(
        registry.dispatch("create_class", {"name": "Warehouse"}, tool_context)
    )
    assert result.success is True

    invalid = asyncio.run(
        registry.dispatch("create_class", {"name": "   "}, tool_context)
    )
    assert invalid.success is False

    unknown = asyncio.run(registry.dispatch("missing", {}, tool_context))
    assert unknown.success is False
    assert "Unknown tool" in unknown.error
