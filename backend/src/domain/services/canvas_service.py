"""Business rules for mutating UML canvas state."""

from uuid import uuid4

from src.domain.models.canvas import (
    Attribute,
    CanvasState,
    ClassDefinition,
    Method,
    Relationship,
    RelationshipType,
)


class CanvasService:
    @staticmethod
    def _require_name(value: str, label: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError(f"{label} must not be empty.")
        return normalized

    @staticmethod
    def _get_class(canvas: CanvasState, class_id: str) -> ClassDefinition:
        class_definition = next(
            (item for item in canvas.classes if item.id == class_id),
            None,
        )
        if class_definition is None:
            raise ValueError(f"Class {class_id} does not exist.")
        return class_definition

    def create_class(self, canvas: CanvasState, name: str) -> ClassDefinition:
        name = self._require_name(name, "Class name")
        if any(existing.name == name for existing in canvas.classes):
            raise ValueError(f"Class {name} already exists.")

        class_definition = ClassDefinition(id=str(uuid4()), name=name)
        canvas.classes.append(class_definition)
        return class_definition

    def delete_class(self, canvas: CanvasState, class_id: str) -> None:
        self._get_class(canvas, class_id)
        canvas.relationships = [
            relationship
            for relationship in canvas.relationships
            if relationship.source_id != class_id
            and relationship.target_id != class_id
        ]
        canvas.classes = [
            class_definition
            for class_definition in canvas.classes
            if class_definition.id != class_id
        ]

    def rename_class(
        self,
        canvas: CanvasState,
        class_id: str,
        new_name: str,
    ) -> ClassDefinition:
        class_definition = self._get_class(canvas, class_id)
        new_name = self._require_name(new_name, "Class name")

        if any(
            existing.id != class_id and existing.name == new_name
            for existing in canvas.classes
        ):
            raise ValueError(f"Class {new_name} already exists.")

        class_definition.name = new_name
        return class_definition

    def add_attribute(
        self,
        canvas: CanvasState,
        class_id: str,
        name: str,
        data_type: str,
        default: str | None = None,
    ) -> Attribute:
        class_definition = self._get_class(canvas, class_id)
        name = self._require_name(name, "Attribute name")
        data_type = self._require_name(data_type, "Attribute type")

        if any(attribute.name == name for attribute in class_definition.attributes):
            raise ValueError(
                f"Attribute {name} already exists in class {class_id}."
            )

        attribute = Attribute(name=name, data_type=data_type, default=default)
        class_definition.attributes.append(attribute)
        return attribute

    def remove_attribute(
        self,
        canvas: CanvasState,
        class_id: str,
        name: str,
    ) -> Attribute:
        class_definition = self._get_class(canvas, class_id)
        name = self._require_name(name, "Attribute name")
        attribute = next(
            (item for item in class_definition.attributes if item.name == name),
            None,
        )
        if attribute is None:
            raise ValueError(f"Attribute {name} does not exist in class {class_id}.")

        class_definition.attributes = [
            item for item in class_definition.attributes if item.name != name
        ]
        return attribute

    def add_method(
        self,
        canvas: CanvasState,
        class_id: str,
        name: str,
        return_type: str,
        parameters: list[str] | None = None,
    ) -> Method:
        class_definition = self._get_class(canvas, class_id)
        name = self._require_name(name, "Method name")
        return_type = self._require_name(return_type, "Method return type")

        if any(method.name == name for method in class_definition.methods):
            raise ValueError(f"Method {name} already exists in class {class_id}.")

        method = Method(
            name=name,
            return_type=return_type,
            parameters=list(parameters or []),
        )
        class_definition.methods.append(method)
        return method

    def remove_method(
        self,
        canvas: CanvasState,
        class_id: str,
        name: str,
    ) -> Method:
        class_definition = self._get_class(canvas, class_id)
        name = self._require_name(name, "Method name")
        method = next(
            (item for item in class_definition.methods if item.name == name),
            None,
        )
        if method is None:
            raise ValueError(f"Method {name} does not exist in class {class_id}.")

        class_definition.methods = [
            item for item in class_definition.methods if item.name != name
        ]
        return method

    def add_relationship(
        self,
        canvas: CanvasState,
        source_id: str,
        target_id: str,
        relation_type: RelationshipType,
    ) -> Relationship:
        self._get_class(canvas, source_id)
        self._get_class(canvas, target_id)
        relation_type = RelationshipType(relation_type)

        if any(
            relationship.source_id == source_id
            and relationship.target_id == target_id
            and relationship.relation_type == relation_type
            for relationship in canvas.relationships
        ):
            raise ValueError(
                f"Relationship {source_id} -> {target_id} "
                f"({relation_type.value}) already exists."
            )

        relationship = Relationship(
            id=str(uuid4()),
            source_id=source_id,
            target_id=target_id,
            relation_type=relation_type,
        )
        canvas.relationships.append(relationship)
        return relationship

    def remove_relationship(
        self,
        canvas: CanvasState,
        source_id: str,
        target_id: str,
        relation_type: RelationshipType,
    ) -> Relationship:
        self._get_class(canvas, source_id)
        self._get_class(canvas, target_id)
        relation_type = RelationshipType(relation_type)

        relationship = next(
            (
                item
                for item in canvas.relationships
                if item.source_id == source_id
                and item.target_id == target_id
                and item.relation_type == relation_type
            ),
            None,
        )
        if relationship is None:
            raise ValueError(
                f"Relationship {source_id} -> {target_id} "
                f"({relation_type.value}) does not exist."
            )

        canvas.relationships = [
            item
            for item in canvas.relationships
            if item.id != relationship.id
        ]
        return relationship
