from .transform_link_base import TransformLinkBase


class TransformRegistry:
    _name_to_class_db: dict[str, type["TransformLinkBase"]] = {}
    """
    A registry for transformation classes.
    Maps class names to transformation class types.
    All links MUST register here, or they wont be serializable.

    Subclasses of TransformLinkBase should register themselves here.
    """

    @staticmethod
    def register_link(class_name: str, transform_class: type["TransformLinkBase"]) -> None:
        """
        Register a transformation class with a name.
        """
        TransformRegistry._name_to_class_db[class_name] = transform_class

    @staticmethod
    def get_link_class(class_name: str) -> type["TransformLinkBase"]:
        """
        Retrieve a transformation class by name.
        """
        if class_name not in TransformRegistry._name_to_class_db:
            raise ValueError(f"Transform '{class_name}' not found in the database.")
        return TransformRegistry._name_to_class_db[class_name]
