"""Validated input schemas for canvas tools."""

from pydantic import BaseModel, ConfigDict, Field

from src.domain.models.canvas import RelationshipType


class ToolInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)


class CreateClassInput(ToolInput):
    name: str = Field(min_length=1)


class DeleteClassInput(ToolInput):
    class_id: str = Field(min_length=1)


class RenameClassInput(ToolInput):
    class_id: str = Field(min_length=1)
    new_name: str = Field(min_length=1)


class AddAttributeInput(ToolInput):
    class_id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    type: str = Field(min_length=1)
    default: str | None = None


class RemoveAttributeInput(ToolInput):
    class_id: str = Field(min_length=1)
    name: str = Field(min_length=1)


class AddRelationshipInput(ToolInput):
    source_id: str = Field(min_length=1)
    target_id: str = Field(min_length=1)
    relationship_type: RelationshipType


class RemoveRelationshipInput(ToolInput):
    source_id: str = Field(min_length=1)
    target_id: str = Field(min_length=1)
    relationship_type: RelationshipType


class AddMethodInput(ToolInput):
    class_id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    return_type: str = Field(min_length=1)
    parameters: list[str] = Field(default_factory=list)


class RemoveMethodInput(ToolInput):
    class_id: str = Field(min_length=1)
    name: str = Field(min_length=1)
