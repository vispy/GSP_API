"""Transform Link Base Module."""
# stdlib imports
from abc import ABC, abstractmethod
from typing import Any

# local imports
from ..types import BufferType, Buffer


# =============================================================================
# TransformLink
# =============================================================================
class TransformLinkBase(ABC):
    """Base class for a link in a Transform chain."""

    @abstractmethod
    def apply(self, buffer_src: Buffer | None) -> Buffer:
        """Apply the transformation to the given buffer and return a new buffer.

        Args:
            buffer_src (Buffer | None): The source buffer to transform. Can be None.

        Returns:
            Buffer: The transformed buffer.
        """
        pass

    @abstractmethod
    def serialize(self) -> dict[str, Any]:
        """Serialize the TransformLink to a dictionary.

        Returns:
            dict[str, Any]: The serialized TransformLink.
        """
        pass

    @staticmethod
    @abstractmethod
    def deserialize(data: dict[str, Any]) -> "TransformLinkBase":
        """Deserialize a TransformLink from a dictionary.

        Args:
            data (dict[str, Any]): The serialized TransformLink.

        Returns:
            TransformLinkBase: The deserialized TransformLink instance.
        """
        pass
