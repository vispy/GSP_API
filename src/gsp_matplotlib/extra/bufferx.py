from gsp.types import Buffer, BufferType
import numpy as np


class Bufferx:
    """Utility class for Buffer extended functionality using numpy."""

    # =============================================================================
    # Matrix functions
    # =============================================================================

    @staticmethod
    def mat4_identity() -> Buffer:
        """Create a Buffer containing a 4x4 identity matrix."""
        mat4_numpy = np.asarray([np.identity(4, dtype=np.float32)])
        buffer = Bufferx.from_numpy(mat4_numpy, BufferType.mat4)
        return buffer

    # =============================================================================
    # .to_numpy/.from_numpy
    # =============================================================================
    @staticmethod
    def to_numpy(buffer: Buffer) -> np.ndarray:
        """Convert a Buffer to a numpy array."""
        if buffer.get_type() == BufferType.float32:
            count = buffer.get_count()
            return np.frombuffer(buffer.to_bytearray(), dtype=np.float32).reshape((count, 1))
        elif buffer.get_type() == BufferType.int8:
            count = buffer.get_count()
            return np.frombuffer(buffer.to_bytearray(), dtype=np.int8).reshape((count, 1))
        elif buffer.get_type() == BufferType.int32:
            count = buffer.get_count()
            return np.frombuffer(buffer.to_bytearray(), dtype=np.int32).reshape((count, 1))
        elif buffer.get_type() == BufferType.uint8:
            count = buffer.get_count()
            return np.frombuffer(buffer.to_bytearray(), dtype=np.uint8).reshape((count, 1))
        elif buffer.get_type() == BufferType.uint32:
            count = buffer.get_count()
            return np.frombuffer(buffer.to_bytearray(), dtype=np.uint32).reshape((count, 1))
        elif buffer.get_type() == BufferType.vec2:
            count = buffer.get_count()
            return np.frombuffer(buffer.to_bytearray(), dtype=np.float32).reshape((count, 2))
        elif buffer.get_type() == BufferType.vec3:
            count = buffer.get_count()
            return np.frombuffer(buffer.to_bytearray(), dtype=np.float32).reshape((count, 3))
        elif buffer.get_type() == BufferType.vec4:
            count = buffer.get_count()
            return np.frombuffer(buffer.to_bytearray(), dtype=np.float32).reshape((count, 4))
        elif buffer.get_type() == BufferType.mat4:
            count = buffer.get_count()
            return np.frombuffer(buffer.to_bytearray(), dtype=np.float32).reshape((count, 4, 4))
        elif buffer.get_type() == BufferType.rgba8:
            count = buffer.get_count()
            return np.frombuffer(buffer.to_bytearray(), dtype=np.uint8).reshape((count, 4))
        else:
            raise NotImplementedError(f"unable to convert buffer {buffer} to numpy array")

    @staticmethod
    def from_numpy(array_numpy: np.ndarray, bufferType: BufferType) -> Buffer:
        """Create a Buffer from a numpy array."""
        if bufferType == BufferType.float32:
            # sanity check
            assert array_numpy.dtype == np.float32, "Numpy array must be of dtype float32"

            count = array_numpy.shape[0]
            buffer = Buffer(count, bufferType)
            buffer.set_data(bytearray(array_numpy.tobytes()), 0, count)
            return buffer
        elif bufferType == BufferType.vec3:
            # sanity check
            assert array_numpy.shape.__len__() == 2 and array_numpy.shape[1] == 3, "Numpy array must be of shape (3,)"

            count = array_numpy.shape[0]
            buffer = Buffer(count, bufferType)
            buffer.set_data(bytearray(array_numpy.astype(np.float32).tobytes()), 0, count)
            return buffer
        elif bufferType == BufferType.mat4:
            # sanity check
            assert array_numpy.shape.__len__() == 3 and array_numpy.shape[1] == 4 and array_numpy.shape[2] == 4, "Numpy array must be of shape (4, 4)"

            count = array_numpy.shape[0]
            buffer = Buffer(count, bufferType)
            buffer.set_data(bytearray(array_numpy.astype(np.float32).tobytes()), 0, 1)
            return buffer
        else:
            raise NotImplementedError(f"unable to create a {bufferType} buffer from numpy array of shape {array_numpy.shape} and dtype {array_numpy.dtype}")
