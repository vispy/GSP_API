# pip imports
from typing import Literal

# local imports
from ...types import BufferType, Buffer
from ..transform_link import TransformLink


TransformAccessorFieldName = Literal["r", "g", "b", "a", "x", "y", "z", "w"]


class TransformAccessor(TransformLink):
    """Access a subset of the input Buffer."""

    def __init__(self, field_name: TransformAccessorFieldName) -> None:
        self._field_name = field_name

    def apply(self, buffer_src: Buffer | None) -> Buffer:
        # sanity check
        assert buffer_src is not None, "Input buffer cannot be None"

        # Map field names to indices
        field_to_index = {"r": 0, "g": 1, "b": 2, "a": 3, "x": 0, "y": 1, "z": 2, "w": 3}
        index = field_to_index[self._field_name]
        item_size = BufferType.get_item_size(buffer_src.get_type())

        # sanity check
        assert buffer_src.get_count() % 4 == 0, f"Input buffer count must be a multiple of 4"

        # Create a new buffer for the accessed field
        new_count = buffer_src.get_count() // 4
        new_buffer = Buffer(new_count, buffer_src.get_type())

        raise NotImplementedError("TransformAccessor.apply is not implemented yet.")
