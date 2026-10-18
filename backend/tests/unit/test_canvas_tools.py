"""State-based tests for the canvas mutation tools."""

import asyncio

import pytest
from src.domain.models.canvas import (
    Attribute,
    CanvasState,
    ClassDefinition,
    Method,
    Relationship,
    RelationshipType,
)
from src.domain.repositories.canvas_repository import CanvasRepository
from src.domain.services.canvas_service import CanvasService
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
    RemoveAttributeInput,
    RemoveMethodInput,
    RemoveRelationshipInput,
    RenameClassInput,
)


@pytest.fixture
def tool_context() -> ToolContext:
    return ToolContext(workspace_id="ws-1", canvas_id="canvas-1")


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


def seed_canvas(
    repository: CanvasRepository,
    context: ToolContext,
    canvas: CanvasState,
) -> None:
    asyncio.run(
        repository.save(context.workspace_id, context.canvas_id, canvas)
    )


def make_tool(tool_type, canvas_service, canvas_repository):
    return tool_type(
        canvas_service=canvas_service,
        canvas_repository=canvas_repository,
    )


def test_create_class_tool_persists_canvas(
    tool_context, canvas_service, canvas_repository
):
    tool = make_tool(CreateClassTool, canvas_service, canvas_repository)
    result = asyncio.run(
        tool.execute(CreateClassInput(name="Order"), tool_context)
    )

    canvas = asyncio.run(
        canvas_repository.get(tool_context.workspace_id, tool_context.canvas_id)
    )
    assert result.success is True
    assert result.data["operation"] == "create_class"
    assert result.data["class_name"] == "Order"
    assert canvas.classes[0].id == result.data["class_id"]
    assert canvas.classes[0].name == "Order"


def test_delete_class_tool_removes_class_and_relationships(
    tool_context, canvas_service, canvas_repository
):
    user = ClassDefinition(id="user", name="User")
    order = ClassDefinition(id="order", name="Order")
    relationship = Relationship(
        id="user-order",
        source_id=user.id,
        target_id=order.id,
        relation_type=RelationshipType.ASSOCIATION,
    )
    seed_canvas(
        canvas_repository,
        tool_context,
        CanvasState(classes=[user, order], relationships=[relationship]),
    )
    tool = make_tool(DeleteClassTool, canvas_service, canvas_repository)

    result = asyncio.run(
        tool.execute(DeleteClassInput(class_id="order"), tool_context)
    )
    canvas = asyncio.run(
        canvas_repository.get(tool_context.workspace_id, tool_context.canvas_id)
    )

    assert result.success is True
    assert result.data["class_id"] == "order"
    assert [item.id for item in canvas.classes] == ["user"]
    assert canvas.relationships == []


def test_rename_class_tool_persists_renamed_class(
    tool_context, canvas_service, canvas_repository
):
    seed_canvas(
        canvas_repository,
        tool_context,
        CanvasState(classes=[ClassDefinition(id="order", name="Order")]),
    )
    tool = make_tool(RenameClassTool, canvas_service, canvas_repository)

    result = asyncio.run(
        tool.execute(
            RenameClassInput(class_id="order", new_name="PurchaseOrder"),
            tool_context,
        )
    )
    canvas = asyncio.run(
        canvas_repository.get(tool_context.workspace_id, tool_context.canvas_id)
    )

    assert result.success is True
    assert result.data["class_id"] == "order"
    assert result.data["new_name"] == "PurchaseOrder"
    assert canvas.classes[0].name == "PurchaseOrder"


def test_add_and_remove_attribute_tools_mutate_state(
    tool_context, canvas_service, canvas_repository
):
    seed_canvas(
        canvas_repository,
        tool_context,
        CanvasState(classes=[ClassDefinition(id="order", name="Order")]),
    )
    add_tool = make_tool(AddAttributeTool, canvas_service, canvas_repository)
    remove_tool = make_tool(RemoveAttributeTool, canvas_service, canvas_repository)

    added = asyncio.run(
        add_tool.execute(
            AddAttributeInput(
                class_id="order",
                name="total",
                type="decimal",
                default="0.00",
            ),
            tool_context,
        )
    )
    canvas = asyncio.run(
        canvas_repository.get(tool_context.workspace_id, tool_context.canvas_id)
    )
    assert added.data["attribute_name"] == "total"
    assert canvas.classes[0].attributes == [
        Attribute(name="total", data_type="decimal", default="0.00")
    ]

    removed = asyncio.run(
        remove_tool.execute(
            RemoveAttributeInput(class_id="order", name="total"),
            tool_context,
        )
    )
    canvas = asyncio.run(
        canvas_repository.get(tool_context.workspace_id, tool_context.canvas_id)
    )
    assert removed.data["attribute_name"] == "total"
    assert canvas.classes[0].attributes == []


def test_add_and_remove_method_tools_mutate_state(
    tool_context, canvas_service, canvas_repository
):
    seed_canvas(
        canvas_repository,
        tool_context,
        CanvasState(classes=[ClassDefinition(id="order", name="Order")]),
    )
    add_tool = make_tool(AddMethodTool, canvas_service, canvas_repository)
    remove_tool = make_tool(RemoveMethodTool, canvas_service, canvas_repository)

    added = asyncio.run(
        add_tool.execute(
            AddMethodInput(
                class_id="order",
                name="calculate_total",
                return_type="decimal",
                parameters=["tax: decimal"],
            ),
            tool_context,
        )
    )
    canvas = asyncio.run(
        canvas_repository.get(tool_context.workspace_id, tool_context.canvas_id)
    )
    assert added.data["method_name"] == "calculate_total"
    assert canvas.classes[0].methods == [
        Method(
            name="calculate_total",
            return_type="decimal",
            parameters=["tax: decimal"],
        )
    ]

    removed = asyncio.run(
        remove_tool.execute(
            RemoveMethodInput(class_id="order", name="calculate_total"),
            tool_context,
        )
    )
    canvas = asyncio.run(
        canvas_repository.get(tool_context.workspace_id, tool_context.canvas_id)
    )
    assert removed.data["method_name"] == "calculate_total"
    assert canvas.classes[0].methods == []


def test_add_and_remove_relationship_tools_mutate_state(
    tool_context, canvas_service, canvas_repository
):
    seed_canvas(
        canvas_repository,
        tool_context,
        CanvasState(
            classes=[
                ClassDefinition(id="user", name="User"),
                ClassDefinition(id="order", name="Order"),
            ]
        ),
    )
    add_tool = make_tool(AddRelationshipTool, canvas_service, canvas_repository)
    remove_tool = make_tool(
        RemoveRelationshipTool, canvas_service, canvas_repository
    )
    params = AddRelationshipInput(
        source_id="user",
        target_id="order",
        relationship_type=RelationshipType.ASSOCIATION,
    )

    added = asyncio.run(add_tool.execute(params, tool_context))
    canvas = asyncio.run(
        canvas_repository.get(tool_context.workspace_id, tool_context.canvas_id)
    )
    assert added.data["relationship_type"] == "association"
    assert len(canvas.relationships) == 1
    assert canvas.relationships[0].id == added.data["relationship_id"]

    removed = asyncio.run(
        remove_tool.execute(
            RemoveRelationshipInput(
                source_id="user",
                target_id="order",
                relationship_type=RelationshipType.ASSOCIATION,
            ),
            tool_context,
        )
    )
    canvas = asyncio.run(
        canvas_repository.get(tool_context.workspace_id, tool_context.canvas_id)
    )
    assert removed.data["relationship_id"] == added.data["relationship_id"]
    assert canvas.relationships == []


def test_registry_validates_inputs_and_returns_domain_failures(
    tool_context, canvas_service, canvas_repository
):
    registry = ToolRegistry()
    registry.register_tool(
        make_tool(CreateClassTool, canvas_service, canvas_repository)
    )
    registry.register_tool(
        make_tool(RenameClassTool, canvas_service, canvas_repository)
    )

    created = asyncio.run(
        registry.dispatch("create_class", {"name": "Order"}, tool_context)
    )
    assert created.success is True

    invalid = asyncio.run(
        registry.dispatch("create_class", {"name": "   "}, tool_context)
    )
    assert invalid.success is False

    duplicate = asyncio.run(
        registry.dispatch("create_class", {"name": "Order"}, tool_context)
    )
    assert duplicate.success is False
    assert "already exists" in duplicate.error

    unknown = asyncio.run(
        registry.dispatch("not_a_tool", {}, tool_context)
    )
    assert unknown.success is False
    assert "Unknown tool" in unknown.error


def test_failed_tool_operation_does_not_mutate_repository_state(
    tool_context, canvas_service, canvas_repository
):
    seed_canvas(
        canvas_repository,
        tool_context,
        CanvasState(
            classes=[
                ClassDefinition(id="user", name="User"),
                ClassDefinition(id="order", name="Order"),
            ]
        ),
    )
    tool = make_tool(RenameClassTool, canvas_service, canvas_repository)

    with pytest.raises(ValueError, match="already exists"):
        asyncio.run(
            tool.execute(
                RenameClassInput(class_id="user", new_name="Order"),
                tool_context,
            )
        )

    canvas = asyncio.run(
        canvas_repository.get(tool_context.workspace_id, tool_context.canvas_id)
    )
    assert {item.id: item.name for item in canvas.classes} == {
        "user": "User",
        "order": "Order",
    }
