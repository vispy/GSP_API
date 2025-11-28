# stdlib imports
import os
from typing import Literal, Any

# pip imports
import requests
import imageio.v3

# local imports
from ...types.buffer import Buffer
from ...types.buffer_type import BufferType
from ..transform_link_base import TransformLinkBase
from ..transform_registry import TransformRegistry


class TransformDataSource(TransformLinkBase):
    """Load data from a URI into a Buffer. previous buffer is ignored."""

    __slots__ = ["_uri", "_buffer_type"]

    def __init__(self, uri: str, buffer_type: BufferType) -> None:
        self._uri = uri
        self._buffer_type = buffer_type

    def apply(self, buffer_src: Buffer | None) -> Buffer:
        item_size = BufferType.get_item_size(self._buffer_type)

        is_image = os.path.splitext(self._uri)[1].lower() in [".png", ".jpg", ".jpeg", ".bmp", ".tiff"]
        if is_image:
            # If the URI points to an image, use imageio to load it

            # Load image data
            image_data = imageio.v3.imread(self._uri)

            # sanity check
            assert image_data.nbytes % item_size == 0, f"Image data size {image_data.nbytes} is not aligned with buffer type item size {item_size}"

            # Build a new buffer
            count = image_data.nbytes // item_size
            new_buffer = Buffer(count, self._buffer_type)
            new_buffer.set_data(bytearray(image_data.tobytes()), 0, count)
            return new_buffer
        else:
            # Load data from URI
            response = requests.get(self._uri)
            response.raise_for_status()
            content = response.content

            # sanity check
            assert len(content) % item_size == 0, f"Data size {len(content)} is not a multiple of item size {item_size} for buffer type {self._buffer_type}"

            count = len(content) // item_size
            new_buffer = Buffer(count, self._buffer_type)
            new_buffer.set_data(bytearray(content), 0, count)
            return new_buffer

    # =============================================================================
    # Serialization functions
    # =============================================================================

    def serialize(self) -> dict[str, Any]:
        return {
            "link_type": "TransformDataSource",
            "link_data": {
                "uri": self._uri,
                "buffer_type": self._buffer_type.name,
            },
        }

    @staticmethod
    def deserialize(data: dict[str, Any]) -> "TransformDataSource":
        assert data["link_type"] == "TransformDataSource", "Invalid type for TransformDataSource deserialization"
        uri: str = data["link_data"]["uri"]
        buffer_type_str: str = data["link_data"]["buffer_type"]
        buffer_type = BufferType[buffer_type_str]
        return TransformDataSource(uri, buffer_type)


# Register the TransformDataSource class in the TransformRegistry
TransformRegistry.register_link("TransformDataSource", TransformDataSource)
