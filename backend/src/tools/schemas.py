from pydantic import BaseModel, Field
from enum import Enum

class RelationshipType(str, Enum):
    inheritance = 'INHERITANCE'
    composition = 'COMPOSITION'
    aggregation = 'AGGREGATION'
    dependency = 'DEPENDENCY'
    association = 'ASSOCIATION'

class CreateClassInput(BaseModel):
    name: str = Field(min_length=1)

class DeleteClassInput(BaseModel):
    class_id: str = Field(min_length=1)

class RenameClassInput(BaseModel):
    class_id: str = Field(min_length=1)
    new_name: str = Field(min_length=1)

class AddAttributeInput(BaseModel):
    class_id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    type: str = Field(min_length=1)
    default:str | None = None

class RemoveAttributeInput(BaseModel):
    class_id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    
class AddRelationshipInput(BaseModel):
    source_id: str = Field(min_length=1)
    target_id: str = Field(min_length=1)
    relationship_type: RelationshipType
class RemoveRelationshipInput(BaseModel):
    source_id: str = Field(min_length=1)
    target_id: str = Field(min_length=1)
    relationship_type: RelationshipType

class AddMethodInput(BaseModel):
    class_id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    return_type: str = Field(min_length=1)
    parameters: list[str] = Field(default_factory=list)


class RemoveMethodInput(BaseModel):
    class_id: str = Field(min_length=1)
    name: str = Field(min_length=1)

