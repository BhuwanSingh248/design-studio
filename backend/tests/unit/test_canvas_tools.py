"""Unit tests for canvas manipulation tools."""
import asyncio
import pytest
from src.tools.base import ToolContext
from src.tools.canvas import (
    AddAttributeTool,
    AddMethodTool,
    AddRelationshipTool,
    CreateClassTool,
    DeleteClassTool,
    RemoveAttributeTool,
    RemoveMethodTool,
    RemoveRelationshipTool,
    RenameClassTool,
)
from src.tools.registry import ToolRegistry
from src.tools.schemas import (
    AddAttributeInput,
    AddMethodInput,
    AddRelationshipInput,
    CreateClassInput,
    DeleteClassInput,
    RelationshipType,
    RemoveAttributeInput,
    RemoveMethodInput,
    RemoveRelationshipInput,
    RenameClassInput,
)


@pytest.fixture
def tool_context():
    return ToolContext(workspace_id="ws-1", canvas_id="canvas-1")


def test_create_class_tool(tool_context):
    tool = CreateClassTool()
    params = CreateClassInput(name="Order")
    result = asyncio.run(tool.execute(params, tool_context))
    assert result.success is True
    assert result.data["class_name"] == "Order"
    assert result.data["canvas_id"] == "canvas-1"


def test_delete_class_tool(tool_context):
    tool = DeleteClassTool()
    params = DeleteClassInput(class_id="class-1")
    result = asyncio.run(tool.execute(params, tool_context))
    assert result.success is True
    assert result.data["class_id"] == "class-1"


def test_rename_class_tool(tool_context):
    tool = RenameClassTool()
    params = RenameClassInput(class_id="class-1", new_name="SpecialOrder")
    result = asyncio.run(tool.execute(params, tool_context))
    assert result.success is True
    assert result.data["new_name"] == "SpecialOrder"


def test_add_attribute_tool(tool_context):
    tool = AddAttributeTool()
    params = AddAttributeInput(class_id="class-1", name="price", type="float", default="0.0")
    result = asyncio.run(tool.execute(params, tool_context))
    assert result.success is True
    assert result.data["attribute_name"] == "price"
    assert result.data["attribute_type"] == "float"


def test_remove_attribute_tool(tool_context):
    tool = RemoveAttributeTool()
    params = RemoveAttributeInput(class_id="class-1", name="price")
    result = asyncio.run(tool.execute(params, tool_context))
    assert result.success is True
    assert result.data["attribute_name"] == "price"


def test_add_method_tool(tool_context):
    tool = AddMethodTool()
    params = AddMethodInput(
        class_id="class-1",
        name="calculate_total",
        return_type="float",
        parameters=["tax: float"],
    )
    result = asyncio.run(tool.execute(params, tool_context))
    assert result.success is True
    assert result.data["method_name"] == "calculate_total"
    assert result.data["parameters"] == ["tax: float"]


def test_remove_method_tool(tool_context):
    tool = RemoveMethodTool()
    params = RemoveMethodInput(class_id="class-1", name="calculate_total")
    result = asyncio.run(tool.execute(params, tool_context))
    assert result.success is True
    assert result.data["method_name"] == "calculate_total"


def test_add_relationship_tool(tool_context):
    tool = AddRelationshipTool()
    params = AddRelationshipInput(
        source_id="class-1",
        target_id="class-2",
        relationship_type=RelationshipType.composition,
    )
    result = asyncio.run(tool.execute(params, tool_context))
    assert result.success is True
    assert result.data["relationship_type"] == "COMPOSITION"


def test_remove_relationship_tool(tool_context):
    tool = RemoveRelationshipTool()
    params = RemoveRelationshipInput(
        source_id="class-1",
        target_id="class-2",
        relationship_type=RelationshipType.composition,
    )
    result = asyncio.run(tool.execute(params, tool_context))
    assert result.success is True
    assert result.data["source_id"] == "class-1"


def test_tool_registry_registration_and_schemas():
    registry = ToolRegistry()
    tool = CreateClassTool()
    registry.register_tool(tool)

    assert registry.get_tool("create_class") is tool

    # Duplicate registration raises error
    with pytest.raises(ValueError, match="Tool create_class already registered"):
        registry.register_tool(tool)

    schemas = registry.schemas
    assert len(schemas["tools"]) == 1
    assert schemas["tools"][0]["name"] == "create_class"
    assert "properties" in schemas["tools"][0]["input_schema"]


def test_tool_registry_dispatch(tool_context):
    registry = ToolRegistry()
    registry.register_tool(CreateClassTool())

    # Valid dispatch
    result = asyncio.run(
        registry.dispatch("create_class", {"name": "Product"}, tool_context)
    )
    assert result.success is True
    assert result.data["class_name"] == "Product"

    # Unknown tool dispatch
    unknown_result = asyncio.run(
        registry.dispatch("non_existent", {}, tool_context)
    )
    assert unknown_result.success is False
    assert "Unknown tool" in unknown_result.error

    # Validation error dispatch (missing required 'name')
    invalid_result = asyncio.run(
        registry.dispatch("create_class", {}, tool_context)
    )
    assert invalid_result.success is False
    assert invalid_result.error is not None
