"""Unit tests for CanvasService."""

import pytest
from src.domain.models.canvas import (
    CanvasState,
    ClassDefinition,
    Relationship,
    RelationshipType,
)
from src.domain.services.canvas_service import CanvasService


@pytest.fixture
def canvas_service() -> CanvasService:
    return CanvasService()


def test_delete_existing_class(canvas_service: CanvasService):
    """1. Delete an existing class."""
    target_class = ClassDefinition(id="cls-user", name="User")
    other_class = ClassDefinition(id="cls-account", name="Account")
    canvas = CanvasState(classes=[target_class, other_class])

    canvas_service.delete_class(canvas, "cls-user")

    assert len(canvas.classes) == 1
    assert canvas.classes[0].id == "cls-account"
    assert all(cls.id != "cls-user" for cls in canvas.classes)


def test_delete_class_raises_value_error_when_class_does_not_exist(
    canvas_service: CanvasService,
):
    """2. Raise ValueError when class doesn't exist."""
    canvas = CanvasState(classes=[ClassDefinition(id="cls-user", name="User")])

    with pytest.raises(ValueError, match="does not exist"):
        canvas_service.delete_class(canvas, "non-existent-id")


def test_delete_class_removes_inbound_relationship(canvas_service: CanvasService):
    """3. Delete class and remove an inbound relationship."""
    user = ClassDefinition(id="cls-user", name="User")
    order = ClassDefinition(id="cls-order", name="Order")
    # Inbound relationship to Order (User -> Order)
    inbound_rel = Relationship(
        id="rel-user-order",
        source_id=user.id,
        target_id=order.id,
        relation_type=RelationshipType.ASSOCIATION,
    )
    canvas = CanvasState(classes=[user, order], relationships=[inbound_rel])

    canvas_service.delete_class(canvas, order.id)

    assert order not in canvas.classes
    assert len(canvas.classes) == 1
    assert canvas.classes[0].id == user.id
    assert len(canvas.relationships) == 0


def test_delete_class_removes_outbound_relationship(canvas_service: CanvasService):
    """4. Delete class and remove an outbound relationship."""
    order = ClassDefinition(id="cls-order", name="Order")
    payment = ClassDefinition(id="cls-payment", name="Payment")
    # Outbound relationship from Order (Order -> Payment)
    outbound_rel = Relationship(
        id="rel-order-payment",
        source_id=order.id,
        target_id=payment.id,
        relation_type=RelationshipType.ASSOCIATION,
    )
    canvas = CanvasState(classes=[order, payment], relationships=[outbound_rel])

    canvas_service.delete_class(canvas, order.id)

    assert order not in canvas.classes
    assert len(canvas.classes) == 1
    assert canvas.classes[0].id == payment.id
    assert len(canvas.relationships) == 0


def test_delete_class_preserves_unrelated_relationship(canvas_service: CanvasService):
    """5. Delete class while preserving an unrelated relationship."""
    user = ClassDefinition(id="cls-user", name="User")
    order = ClassDefinition(id="cls-order", name="Order")
    product = ClassDefinition(id="cls-product", name="Product")
    category = ClassDefinition(id="cls-category", name="Category")

    # User -> Order
    rel_user_order = Relationship(
        id="rel-user-order",
        source_id=user.id,
        target_id=order.id,
        relation_type=RelationshipType.ASSOCIATION,
    )
    # Product -> Category (unrelated)
    rel_product_category = Relationship(
        id="rel-product-category",
        source_id=product.id,
        target_id=category.id,
        relation_type=RelationshipType.ASSOCIATION,
    )

    canvas = CanvasState(
        classes=[user, order, product, category],
        relationships=[rel_user_order, rel_product_category],
    )

    canvas_service.delete_class(canvas, order.id)

    # Order is removed, User, Product, Category remain
    assert order not in canvas.classes
    remaining_class_ids = {cls.id for cls in canvas.classes}
    assert remaining_class_ids == {user.id, product.id, category.id}

    # User -> Order is deleted, Product -> Category is preserved
    assert len(canvas.relationships) == 1
    assert canvas.relationships[0].id == rel_product_category.id
    assert canvas.relationships[0].source_id == product.id
    assert canvas.relationships[0].target_id == category.id
