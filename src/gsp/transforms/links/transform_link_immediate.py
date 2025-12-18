"""Transform link that immediately returns a predefined buffer.

This module provides a TransformLink implementation that returns a fixed buffer
without any transformation, useful for providing constant data in transform chains.
"""

# pip imports
from typing import Literal, Any
import base64

# local imports
from gsp.transforms.transform_registry import TransformRegistry
from gsp.transforms.transform_link_base import TransformLinkBase
from gsp.types import BufferType, Buffer


class TransformLinkImmediate(TransformLinkBase):
    """A TransformLink that immediately returns a predefined Buffer."""

    def __init__(self, buffer: Buffer) -> None:
        """Initialize the immediate transform link with a buffer.

        Args:
            buffer: The buffer to return when apply() is called.
        """
        self._buffer = buffer

    def apply(self, buffer_src: Buffer | None) -> Buffer:
        """Return the predefined buffer, ignoring the source buffer.

        Args:
            buffer_src: Source buffer (ignored).

        Returns:
            The predefined buffer set during initialization.
        """
        return self._buffer

    # =============================================================================
    # Serialization functions
    # =============================================================================

    def serialize(self) -> dict[str, Any]:
        """Serialize the transform link to a dictionary.

        Returns:
            A dictionary containing the link type and buffer data encoded in base64.
        """
        data_base64 = base64.b64encode(self._buffer.to_bytearray()).decode("utf-8")
        return {
            "link_type": "TransformImmediate",
            "link_data": {
                "buffer_count": self._buffer.get_count(),
                "buffer_type": self._buffer.get_type().name,
                "data_base64": data_base64,
            },
        }

    @staticmethod
    def deserialize(data: dict[str, Any]) -> "TransformLinkImmediate":
        """Deserialize a transform link from a dictionary.

        Args:
            data: Dictionary containing serialized link data with link_type and link_data fields.

        Returns:
            A new TransformLinkImmediate instance with the deserialized buffer.

        Raises:
            AssertionError: If the link_type is not 'TransformImmediate'.
        """
        assert data["link_type"] == "TransformImmediate", "Invalid type for TransformImmediate deserialization"
        buffer_count = int(data["link_data"]["buffer_count"])
        buffer_type_str: str = data["link_data"]["buffer_type"]
        buffer_type = BufferType[buffer_type_str]
        data_base64: str = data["link_data"]["data_base64"]
        data_bytes: bytes = base64.b64decode(data_base64.encode("utf-8"))

        buffer = Buffer(buffer_count, buffer_type)
        buffer.set_data(bytearray(data_bytes), 0, buffer_count)

        return TransformLinkImmediate(buffer)


# Register the TransformImmediate class in the TransformRegistry
TransformRegistry.register_link("TransformImmediate", TransformLinkImmediate)
