"""Unit tests for CanvasService business rules."""

import pytest
from src.domain.models.canvas import (
    Attribute,
    CanvasState,
    ClassDefinition,
    Method,
    Relationship,
    RelationshipType,
)
from src.domain.services.canvas_service import CanvasService


@pytest.fixture
def canvas_service() -> CanvasService:
    return CanvasService()


def test_delete_existing_class(canvas_service: CanvasService):
    target_class = ClassDefinition(id="cls-user", name="User")
    other_class = ClassDefinition(id="cls-account", name="Account")
    canvas = CanvasState(classes=[target_class, other_class])

    canvas_service.delete_class(canvas, "cls-user")

    assert [cls.id for cls in canvas.classes] == ["cls-account"]


def test_delete_class_raises_for_missing_class(canvas_service: CanvasService):
    canvas = CanvasState(classes=[ClassDefinition(id="cls-user", name="User")])

    with pytest.raises(ValueError, match="does not exist"):
        canvas_service.delete_class(canvas, "missing")


def test_delete_class_removes_related_relationships(canvas_service: CanvasService):
    user = ClassDefinition(id="user", name="User")
    order = ClassDefinition(id="order", name="Order")
    unrelated = Relationship(
        id="unrelated",
        source_id="product",
        target_id="category",
        relation_type=RelationshipType.ASSOCIATION,
    )
    related = Relationship(
        id="related",
        source_id=user.id,
        target_id=order.id,
        relation_type=RelationshipType.ASSOCIATION,
    )
    canvas = CanvasState(
        classes=[user, order],
        relationships=[related, unrelated],
    )

    canvas_service.delete_class(canvas, order.id)

    assert [item.id for item in canvas.classes] == ["user"]
    assert [item.id for item in canvas.relationships] == ["unrelated"]


def test_create_and_rename_class_enforce_unique_names(canvas_service: CanvasService):
    canvas = CanvasState()
    created = canvas_service.create_class(canvas, "  Order  ")
    other = canvas_service.create_class(canvas, "Customer")
    assert created.name == "Order"

    with pytest.raises(ValueError, match="already exists"):
        canvas_service.create_class(canvas, "Order")

    with pytest.raises(ValueError, match="already exists"):
        canvas_service.rename_class(canvas, created.id, other.name)

    with pytest.raises(ValueError, match="must not be empty"):
        canvas_service.rename_class(canvas, created.id, "   ")


def test_add_attribute_requires_existing_class_and_unique_name(
    canvas_service: CanvasService,
):
    target = ClassDefinition(id="order", name="Order")
    canvas = CanvasState(classes=[target])

    attribute = canvas_service.add_attribute(
        canvas, "order", "total", "decimal", "0.00"
    )
    assert attribute == Attribute(
        name="total",
        data_type="decimal",
        default="0.00",
    )

    with pytest.raises(ValueError, match="already exists"):
        canvas_service.add_attribute(canvas, "order", "total", "float")

    with pytest.raises(ValueError, match="does not exist"):
        canvas_service.add_attribute(canvas, "missing", "id", "int")


def test_remove_attribute_returns_removed_attribute(canvas_service: CanvasService):
    target = ClassDefinition(
        id="order",
        name="Order",
        attributes=[Attribute(name="total", data_type="decimal")],
    )
    canvas = CanvasState(classes=[target])

    removed = canvas_service.remove_attribute(canvas, "order", "total")

    assert removed.name == "total"
    assert target.attributes == []
    with pytest.raises(ValueError, match="does not exist"):
        canvas_service.remove_attribute(canvas, "order", "total")


def test_add_and_remove_method(canvas_service: CanvasService):
    target = ClassDefinition(id="order", name="Order")
    canvas = CanvasState(classes=[target])

    method = canvas_service.add_method(
        canvas,
        "order",
        "calculate_total",
        "decimal",
        ["tax: decimal"],
    )
    assert method == Method(
        name="calculate_total",
        return_type="decimal",
        parameters=["tax: decimal"],
    )

    with pytest.raises(ValueError, match="already exists"):
        canvas_service.add_method(canvas, "order", "calculate_total", "decimal")

    removed = canvas_service.remove_method(canvas, "order", "calculate_total")
    assert removed.name == "calculate_total"
    assert target.methods == []

    with pytest.raises(ValueError, match="does not exist"):
        canvas_service.remove_method(canvas, "order", "calculate_total")


@pytest.mark.parametrize("relation_type", list(RelationshipType))
def test_add_relationship_supports_canonical_types(
    canvas_service: CanvasService,
    relation_type: RelationshipType,
):
    canvas = CanvasState(
        classes=[
            ClassDefinition(id="source", name="Source"),
            ClassDefinition(id="target", name="Target"),
        ]
    )

    relationship = canvas_service.add_relationship(
        canvas, "source", "target", relation_type
    )

    assert relationship.relation_type is relation_type


def test_add_relationship_validates_endpoints_and_duplicates(
    canvas_service: CanvasService,
):
    user = ClassDefinition(id="user", name="User")
    order = ClassDefinition(id="order", name="Order")
    canvas = CanvasState(classes=[user, order])

    canvas_service.add_relationship(
        canvas, "user", "order", RelationshipType.ASSOCIATION
    )

    with pytest.raises(ValueError, match="already exists"):
        canvas_service.add_relationship(
            canvas, "user", "order", RelationshipType.ASSOCIATION
        )

    with pytest.raises(ValueError, match="does not exist"):
        canvas_service.add_relationship(
            canvas, "user", "missing", RelationshipType.ASSOCIATION
        )


def test_remove_relationship_matches_endpoints_and_type(
    canvas_service: CanvasService,
):
    user = ClassDefinition(id="user", name="User")
    order = ClassDefinition(id="order", name="Order")
    canvas = CanvasState(classes=[user, order])
    relationship = canvas_service.add_relationship(
        canvas, "user", "order", RelationshipType.COMPOSITION
    )

    removed = canvas_service.remove_relationship(
        canvas, "user", "order", RelationshipType.COMPOSITION
    )
    assert removed.id == relationship.id
    assert canvas.relationships == []

    with pytest.raises(ValueError, match="does not exist"):
        canvas_service.remove_relationship(
            canvas, "user", "order", RelationshipType.COMPOSITION
        )
