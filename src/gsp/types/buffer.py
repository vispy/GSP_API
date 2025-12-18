"""Buffer module for typed array with single dimension."""

# stdlib imports
from enum import Enum

# pip imports
import numpy as np

# local imports
from .buffer_type import BufferType


class Buffer:
    """Typed array with single dimension.

    It is immutable in count and type, but mutable in content.
    """

    def __init__(self, count: int, buffer_type: BufferType) -> None:
        """Initialize a Buffer instance.

        Args:
            count (int): The number of elements in the buffer.
            buffer_type (BufferType): The type of elements in the buffer.
        """
        item_size = BufferType.get_item_size(buffer_type)
        self._count: int = count
        self._type: BufferType = buffer_type
        self._bytearray: bytearray = bytearray(count * item_size)

    def __repr__(self) -> str:
        """Return a string representation of the Buffer.

        Returns:
            str: A string representation showing count and type.
        """
        return f"Buffer(count={self._count}, type={self._type})"

    def get_count(self) -> int:
        """Return the number of elements in the buffer.

        Returns:
            int: The number of elements.
        """
        return self._count

    def get_type(self) -> BufferType:
        """Return the type of each element in the buffer.

        Returns:
            BufferType: The buffer type.
        """
        return self._type

    # =============================================================================
    # .get_data/.set_data
    # =============================================================================

    def get_data(self, offset: int, count: int) -> "Buffer":
        """Return a buffer of count elements starting from offset.

        Args:
            offset (int): The starting index.
            count (int): The number of elements to retrieve.

        Returns:
            Buffer: A new Buffer containing the requested data.
        """
        item_size = BufferType.get_item_size(self._type)
        start = offset * item_size
        end = start + count * item_size

        new_buffer = Buffer(count, self._type)
        new_buffer.set_data(self._bytearray[start:end], 0, count)
        return new_buffer

    def set_data(self, _bytearray: bytearray, offset: int, count: int) -> None:
        """Copy count elements starting from offset in the source bytearray.

        Args:
            _bytearray (bytearray): The source bytearray containing data to copy.
            offset (int): The starting index in the buffer where data will be copied.
            count (int): The number of elements to copy.
        """
        item_size = BufferType.get_item_size(self._type)

        # sanity check
        assert offset + count <= self._count, f"Invalid offset {offset} and count {count} for buffer of size {self._count}"

        start = offset * item_size
        end = start + count * item_size
        self._bytearray = self._bytearray[:start] + _bytearray[0 : count * item_size] + self._bytearray[end:]

    # =============================================================================
    # .to_bytearray/from_bytearray
    # =============================================================================

    def to_bytearray(self) -> bytearray:
        """Return the content of the Buffer as a bytearray.

        Returns:
            bytearray: The bytearray representation of the Buffer.
        """
        return bytearray(self._bytearray)

    @staticmethod
    def from_bytearray(_bytearray: bytearray, buffer_type: BufferType) -> "Buffer":
        """Create a Buffer from a bytearray and a specified BufferType.

        Args:
            _bytearray (bytearray): The source bytearray.
            buffer_type (BufferType): The type of elements in the buffer.

        Returns:
            Buffer: The created Buffer instance.
        """
        item_size = BufferType.get_item_size(buffer_type)
        # sanity check
        assert len(_bytearray) % item_size == 0, f"data size {len(_bytearray)} is not aligned with buffer type item size {item_size}"

        # create buffer
        buffer = Buffer(len(_bytearray) // item_size, buffer_type)
        buffer.set_data(_bytearray, 0, buffer.get_count())
        return buffer
