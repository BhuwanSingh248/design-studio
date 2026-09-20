from uuid import uuid4
from src.domain.models.canvas import CanvasState, ClassDefinition

class CanvasService:
    def __init__(self):
        self.class_map: dict[str, ClassDefinition] = {}


    def create_class(self, canvas: CanvasState, name:str) -> ClassDefinition:
        if any(existing.name == name for existing in canvas.classes):
            raise ValueError(f"Class {name} already exists.")
        
        class_id=str(uuid4())
        class_definition = ClassDefinition(
            id=class_id,
            name=name
        )

        canvas.classes.append(class_definition)
        return class_definition

    def delete_class(self, canvas: CanvasState, class_id: str) -> None:
        # need to takecare of
        #  if order  ----> payments : delete payments
        # then order  ----> ???? which will be an invalid  canvas state so we need to remove the relationship also.
        # so first we need to remove the relationship and then remove the class.

        
        class_exist = any(cls.id == class_id for cls in canvas.classes)
        if not class_exist:
            raise ValueError(f"Class {class_id} does not exist.")
        
        # remove relationship

        canvas.relationships = [
            relationship 
            for relationship in canvas.relationships
            if (
                relationship.source_id == class_id and relationship.target_id == class_id
            ) 
        ]

        # remove the class
        canvas.classes = [cls for cls in canvas.classes if cls.id != class_id]

