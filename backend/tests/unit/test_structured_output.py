"""Unit tests for domain models and structured schema validation."""
from src.domain.models.canvas import Attribute, ClassDefinition, Visibility


def test_attribute_uml_string():
    attr = Attribute(name="email", data_type="str", visibility=Visibility.PRIVATE)
    assert attr.to_uml_string() == "- email: str"


def test_class_definition_creation():
    cls = ClassDefinition(id="c1", name="User")
    assert cls.name == "User"
    assert len(cls.attributes) == 0
