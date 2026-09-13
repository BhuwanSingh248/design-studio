"""Canonical domain models for UML class diagrams."""
from enum import Enum
from pydantic import BaseModel, Field


class Visibility(str, Enum):
    PUBLIC = "+"
    PRIVATE = "-"
    PROTECTED = "#"
    PACKAGE = "~"


class Stereotype(str, Enum):
    ENTITY = "entity"
    VALUE_OBJECT = "value_object"
    SERVICE = "service"
    INTERFACE = "interface"
    ABSTRACT = "abstract"


class RelationshipType(str, Enum):
    ASSOCIATION = "association"
    AGGREGATION = "aggregation"
    COMPOSITION = "composition"
    INHERITANCE = "inheritance"
    REALIZATION = "realization"


class Attribute(BaseModel):
    name: str
    data_type: str = "str"
    visibility: Visibility = Visibility.PUBLIC

    def to_uml_string(self) -> str:
        return f"{self.visibility.value} {self.name}: {self.data_type}"


class Method(BaseModel):
    name: str
    return_type: str = "void"
    visibility: Visibility = Visibility.PUBLIC
    parameters: list[str] = Field(default_factory=list)

    def to_signature_string(self) -> str:
        params = ", ".join(self.parameters)
        return f"{self.visibility.value} {self.name}({params}): {self.return_type}"


class ClassDefinition(BaseModel):
    id: str
    name: str
    stereotype: Stereotype = Stereotype.ENTITY
    attributes: list[Attribute] = Field(default_factory=list)
    methods: list[Method] = Field(default_factory=list)
    position_x: float = 0.0
    position_y: float = 0.0


class Relationship(BaseModel):
    id: str
    source_id: str
    target_id: str
    relation_type: RelationshipType
    source_multiplicity: str | None = None
    target_multiplicity: str | None = None


class CanvasState(BaseModel):
    classes: list[ClassDefinition] = Field(default_factory=list)
    relationships: list[Relationship] = Field(default_factory=list)
