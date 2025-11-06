# stdlib imports
from enum import Enum

# pip imports
import numpy as np

# local imports
from .buffer_type import BufferType


class Buffer:
    """typed array with single dimension
    - it is immutable in count and type, but mutable in content
    """

    def __init__(self, count: int, buffer_type: BufferType) -> None:
        item_size = BufferType.get_item_size(buffer_type)
        self._count: int = count
        self._type: BufferType = buffer_type
        self._bytearray: bytearray = bytearray(count * item_size)

    def __repr__(self) -> str:
        return f"Buffer(count={self._count}, type={self._type})"

    def get_count(self) -> int:
        """Return the number of elements in the buffer."""
        return self._count

    def get_type(self) -> BufferType:
        """Return the type of each element in the buffer."""
        return self._type

    # =============================================================================
    # .get_data/.set_data
    # =============================================================================

    def get_data(self, offset: int, count: int) -> "Buffer":
        """Return a buffer of count elements starting from offset."""
        item_size = BufferType.get_item_size(self._type)
        start = offset * item_size
        end = start + count * item_size

        new_buffer = Buffer(count, self._type)
        new_buffer.set_data(self._bytearray[start:end], 0, count)
        return new_buffer

    def set_data(self, _bytearray: bytearray, offset: int, count: int) -> None:
        """Copy count elements starting from offset in the source bytearray."""
        item_size = BufferType.get_item_size(self._type)

        # sanity check
        assert offset + count <= self._count, f"Invalid offset {offset} and count {count} for buffer of size {self._count}"

        start = offset * item_size
        end = start + count * item_size
        self._bytearray = self._bytearray[:start] + _bytearray[0 : count * item_size] + self._bytearray[end:]

    # # =============================================================================
    # # .to_numpy/.from_numpy
    # # =============================================================================

    # # numpy conversion
    # def to_numpy(self) -> np.ndarray:
    #     if self.get_type() == BufferType.rgba8:
    #         # Special case for color buffer: interpret as uint8 and reshape
    #         numpy_dtype = np.dtype(np.uint8)
    #         ndarray = np.frombuffer(self._bytearray, dtype=numpy_dtype).reshape(
    #             (self._count, 4)
    #         )
    #         return ndarray

    #     numpy_dtype = BufferType.to_numpy_dtype(self._type)
    #     numpy_shape = BufferType.to_numpy_shape(self._type)
    #     ndarray = np.frombuffer(self._bytearray, dtype=numpy_dtype).reshape(
    #         (self._count,) + numpy_shape
    #     )
    #     return ndarray

    # @staticmethod
    # def from_numpy(ndarray: np.ndarray) -> "Buffer":
    #     buffer_type = BufferType.from_numpy(ndarray)
    #     count = ndarray.shape[0]

    #     buffer = Buffer(count, buffer_type)
    #     buffer.set_data(bytearray(ndarray.tobytes()), 0, buffer.get_count())
    #     return buffer

    # =============================================================================
    # .to_bytearray/from_bytearray
    # =============================================================================

    def to_bytearray(self) -> bytearray:
        return bytearray(self._bytearray)

    @staticmethod
    def from_bytearray(_bytearray: bytearray, buffer_type: BufferType) -> "Buffer":
        item_size = BufferType.get_item_size(buffer_type)
        # sanity check
        assert len(_bytearray) % item_size == 0, f"data size {len(_bytearray)} is not aligned with buffer type item size {item_size}"

        # create buffer
        buffer = Buffer(len(_bytearray) // item_size, buffer_type)
        buffer.set_data(_bytearray, 0, buffer.get_count())
        return buffer
