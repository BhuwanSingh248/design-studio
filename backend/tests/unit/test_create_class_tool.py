"""Unit tests for CreateClassTool."""
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
    repo = CanvasRepository()
    canvas = CanvasState()
    asyncio.run(repo.save(tool_context.canvas_id, canvas))
    return repo


@pytest.fixture
def create_class_tool(
    canvas_service: CanvasService,
    canvas_repository: CanvasRepository,
) -> CreateClassTool:
    return CreateClassTool(
        canvas_service=canvas_service,
        canvas_repository=canvas_repository,
    )


# =====================================================================
# 1. Metadata and Initialization Tests
# =====================================================================

def test_create_class_tool_metadata(create_class_tool: CreateClassTool):
    """Test tool attributes and schema configuration."""
    assert create_class_tool.name == "create_class"
    assert create_class_tool.description == "Create a new class on the design canvas."
    assert create_class_tool.input_schema is CreateClassInput


# =====================================================================
# 2. Execution Tests (Direct Call)
# =====================================================================

def test_execute_success(
    create_class_tool: CreateClassTool,
    canvas_repository: CanvasRepository,
    tool_context: ToolContext,
):
    """Test creating a class successfully updates canvas and returns correct ToolResult."""
    params = CreateClassInput(name="Order")
    result = asyncio.run(create_class_tool.execute(params, tool_context))

    assert result.success is True
    assert result.error is None
    assert result.data["operation"] == "create_class"
    assert result.data["class_name"] == "Order"
    assert isinstance(result.data["class_id"], str)
    assert len(result.data["class_id"]) > 0
    assert result.data["workspace_id"] == "ws-123"
    assert result.data["canvas_id"] == "canvas-456"

    # Verify canvas state in repository was actually updated
    canvas = asyncio.run(canvas_repository.get("canvas-456"))
    assert len(canvas.classes) == 1
    assert canvas.classes[0].name == "Order"
    assert canvas.classes[0].id == result.data["class_id"]


def test_execute_multiple_classes(
    create_class_tool: CreateClassTool,
    canvas_repository: CanvasRepository,
    tool_context: ToolContext,
):
    """Test creating multiple classes sequentially generates unique IDs."""
    result1 = asyncio.run(
        create_class_tool.execute(CreateClassInput(name="Customer"), tool_context)
    )
    result2 = asyncio.run(
        create_class_tool.execute(CreateClassInput(name="Invoice"), tool_context)
    )

    assert result1.success is True
    assert result2.success is True
    assert result1.data["class_id"] != result2.data["class_id"]

    canvas = asyncio.run(canvas_repository.get(tool_context.canvas_id))
    assert len(canvas.classes) == 2
    class_names = [cls.name for cls in canvas.classes]
    assert "Customer" in class_names
    assert "Invoice" in class_names


def test_execute_duplicate_class_raises_value_error(
    create_class_tool: CreateClassTool,
    tool_context: ToolContext,
):
    """Test that creating a class with an existing name raises ValueError."""
    asyncio.run(create_class_tool.execute(CreateClassInput(name="Product"), tool_context))

    with pytest.raises(ValueError, match="Class Product already exists."):
        asyncio.run(
            create_class_tool.execute(CreateClassInput(name="Product"), tool_context)
        )


def test_execute_canvas_not_found_raises_value_error(
    create_class_tool: CreateClassTool,
):
    """Test executing on a non-existent canvas raises ValueError."""
    missing_context = ToolContext(workspace_id="ws-1", canvas_id="nonexistent-canvas")
    with pytest.raises(ValueError, match="Canvas nonexistent-canvas not found"):
        asyncio.run(
            create_class_tool.execute(CreateClassInput(name="Account"), missing_context)
        )


# =====================================================================
# 3. Unit Isolation Tests (Mocked Dependencies)
# =====================================================================

def test_execute_with_mocked_dependencies(tool_context: ToolContext):
    """Test tool interaction with CanvasRepository and CanvasService in isolation."""
    mock_repo = AsyncMock(spec=CanvasRepository)
    mock_service = MagicMock(spec=CanvasService)

    fake_canvas = CanvasState()
    mock_repo.get.return_value = fake_canvas

    fake_created_class = ClassDefinition(id="fake-uuid-123", name="Payment")
    mock_service.create_class.return_value = fake_created_class

    tool = CreateClassTool(
        canvas_service=mock_service,
        canvas_repository=mock_repo,
    )

    params = CreateClassInput(name="Payment")
    result = asyncio.run(tool.execute(params, tool_context))

    # Verify dependency invocations
    mock_repo.get.assert_awaited_once_with(tool_context.canvas_id)
    mock_service.create_class.assert_called_once_with(fake_canvas, "Payment")

    assert result.success is True
    assert result.data["class_name"] == "Payment"
    assert result.data["class_id"] == "fake-uuid-123"
    assert result.data["canvas_id"] == tool_context.canvas_id
    assert result.data["workspace_id"] == tool_context.workspace_id


# =====================================================================
# 4. ToolRegistry Integration Tests (Dispatch & Validation)
# =====================================================================

def test_tool_registry_registration_and_schemas(create_class_tool: CreateClassTool):
    """Test registering tool in ToolRegistry and inspecting generated schemas."""
    registry = ToolRegistry()
    registry.register_tool(create_class_tool)

    assert registry.get_tool("create_class") is create_class_tool

    # Duplicate registration raises error
    with pytest.raises(ValueError, match="Tool create_class already registered"):
        registry.register_tool(create_class_tool)

    schemas = registry.schemas
    assert len(schemas["tools"]) == 1
    tool_schema = schemas["tools"][0]
    assert tool_schema["name"] == "create_class"
    assert tool_schema["description"] == "Create a new class on the design canvas."
    assert "properties" in tool_schema["input_schema"]
    assert "name" in tool_schema["input_schema"]["properties"]


def test_tool_registry_dispatch_success(
    create_class_tool: CreateClassTool,
    canvas_repository: CanvasRepository,
    tool_context: ToolContext,
):
    """Test successful dispatch through ToolRegistry."""
    registry = ToolRegistry()
    registry.register_tool(create_class_tool)

    result = asyncio.run(
        registry.dispatch("create_class", {"name": "Warehouse"}, tool_context)
    )

    assert result.success is True
    assert result.data["class_name"] == "Warehouse"
    assert result.data["canvas_id"] == tool_context.canvas_id

    canvas = asyncio.run(canvas_repository.get(tool_context.canvas_id))
    assert any(cls.name == "Warehouse" for cls in canvas.classes)


def test_tool_registry_dispatch_missing_params(
    create_class_tool: CreateClassTool,
    tool_context: ToolContext,
):
    """Test registry dispatch failure when required parameters are missing."""
    registry = ToolRegistry()
    registry.register_tool(create_class_tool)

    result = asyncio.run(registry.dispatch("create_class", {}, tool_context))
    assert result.success is False
    assert result.error is not None
    assert "name" in result.error


def test_tool_registry_dispatch_empty_name_validation_error(
    create_class_tool: CreateClassTool,
    tool_context: ToolContext,
):
    """Test registry dispatch failure when name violates min_length=1."""
    registry = ToolRegistry()
    registry.register_tool(create_class_tool)

    result = asyncio.run(registry.dispatch("create_class", {"name": ""}, tool_context))
    assert result.success is False
    assert result.error is not None


def test_tool_registry_dispatch_duplicate_class_error(
    create_class_tool: CreateClassTool,
    tool_context: ToolContext,
):
    """Test registry gracefully catches duplicate class domain error and returns error result."""
    registry = ToolRegistry()
    registry.register_tool(create_class_tool)

    # First dispatch succeeds
    res1 = asyncio.run(registry.dispatch("create_class", {"name": "User"}, tool_context))
    assert res1.success is True

    # Second dispatch with same name returns failure ToolResult
    res2 = asyncio.run(registry.dispatch("create_class", {"name": "User"}, tool_context))
    assert res2.success is False
    assert "Class User already exists." in res2.error


def test_tool_registry_dispatch_canvas_not_found_error(
    create_class_tool: CreateClassTool,
):
    """Test registry gracefully catches missing canvas error and returns error result."""
    registry = ToolRegistry()
    registry.register_tool(create_class_tool)

    missing_context = ToolContext(workspace_id="ws-1", canvas_id="unknown-canvas")
    result = asyncio.run(
        registry.dispatch("create_class", {"name": "User"}, missing_context)
    )

    assert result.success is False
    assert "Canvas unknown-canvas not found" in result.error
