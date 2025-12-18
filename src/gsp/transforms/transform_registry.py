"""Registry for transformation link classes.

This module provides a centralized registry for transformation classes,
enabling serialization and deserialization of transform links by name.
"""

from .transform_link_base import TransformLinkBase


class TransformRegistry:
    """A registry for transformation classes.

    Maps class names to transformation class types. All transformation links
    MUST register here, or they won't be serializable.

    Subclasses of TransformLinkBase should register themselves using the
    register_link method to enable serialization and lookup by name.

    Attributes:
        _name_to_class_db: Internal mapping from class names to transformation
            class types.
    """

    _name_to_class_db: dict[str, type["TransformLinkBase"]] = {}

    @staticmethod
    def register_link(class_name: str, transform_class: type["TransformLinkBase"]) -> None:
        """Register a transformation class with a name.

        Args:
            class_name: The name to register the class under.
            transform_class: The transformation class to register.
        """
        TransformRegistry._name_to_class_db[class_name] = transform_class

    @staticmethod
    def get_link_class(class_name: str) -> type["TransformLinkBase"]:
        """Retrieve a transformation class by name.

        Args:
            class_name: The name of the transformation class to retrieve.

        Returns:
            The transformation class associated with the given name.

        Raises:
            ValueError: If the class name is not found in the registry.
        """
        if class_name not in TransformRegistry._name_to_class_db:
            raise ValueError(f"Transform '{class_name}' not found in the database.")
        return TransformRegistry._name_to_class_db[class_name]
