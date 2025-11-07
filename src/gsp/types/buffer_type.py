# stdlib imports
from enum import Enum

# pip imports
import numpy as np
from dataclasses import dataclass


class BufferType(Enum):
    """Type of elements in a Buffer. Heavily inspired by GLSL types and numpy."""

    float32 = 0
    uint32 = 1
    uint8 = 2
    int32 = 3
    int8 = 4
    vec2 = 5
    """vector of 2 float32."""
    vec3 = 6
    """vector of 3 float32."""
    vec4 = 7
    """vector of 4 float32."""
    uvec4 = 8
    """vector of 4 uint32."""
    mat4 = 9  # 4x4 matrix
    """Matrix 4x4 of float32. Column-major order."""
    rgba8 = 10  # RGBA
    """4 unsigned bytes representing red, green, blue, alpha channels. each channel in [0, 255]."""

    @staticmethod
    def get_item_size(buffer_type: "BufferType") -> int:
        """Return the size in bytes of a single item of the given BufferType."""
        if buffer_type == BufferType.float32:
            return 4
        elif buffer_type == BufferType.uint32:
            return 4
        elif buffer_type == BufferType.uint8:
            return 1
        elif buffer_type == BufferType.int32:
            return 4
        elif buffer_type == BufferType.int8:
            return 1
        elif buffer_type == BufferType.vec2:
            return 8  # 2 * 4 bytes (float32)
        elif buffer_type == BufferType.vec3:
            return 12  # 3 * 4 bytes (float32)
        elif buffer_type == BufferType.vec4:
            return 16  # 4 * 4 bytes (float32)
        elif buffer_type == BufferType.uvec4:
            return 16  # 4 * 4 bytes (uint32)
        elif buffer_type == BufferType.rgba8:
            return 4
        elif buffer_type == BufferType.mat4:
            return 64  # 16 * 4 bytes (float32)
        else:
            raise ValueError(f"Unknown BufferType: {buffer_type}")

    @staticmethod
    def to_numpy_dtype(buffer_type: "BufferType") -> np.dtype:
        if buffer_type == BufferType.float32:
            return np.dtype(np.float32)
        elif buffer_type == BufferType.uint32:
            return np.dtype(np.uint32)
        elif buffer_type == BufferType.uint8:
            return np.dtype(np.uint8)
        elif buffer_type == BufferType.int32:
            return np.dtype(np.int32)
        elif buffer_type == BufferType.int8:
            return np.dtype(np.int8)
        elif buffer_type in (BufferType.vec2, BufferType.vec3, BufferType.vec4):
            return np.dtype(np.float32)
        elif buffer_type == BufferType.rgba8:
            return np.dtype(np.uint32)
        else:
            raise ValueError(f"Unknown BufferType: {buffer_type}")

    @staticmethod
    def from_numpy(ndarray: np.ndarray) -> "BufferType":
        if len(ndarray.shape) == 2 and ndarray.dtype == np.dtype(np.float32) and ndarray.shape[1] == 2:
            return BufferType.vec2
        elif len(ndarray.shape) == 2 and ndarray.dtype == np.dtype(np.float32) and ndarray.shape[1] == 3:
            return BufferType.vec3
        elif len(ndarray.shape) == 2 and ndarray.dtype == np.dtype(np.float32) and ndarray.shape[1] == 4:
            return BufferType.vec4
        elif len(ndarray.shape) == 1 and ndarray.dtype == np.dtype(np.float32):
            return BufferType.float32
        else:
            raise ValueError(f"Cannot convert numpy dtype to BufferType")

    @staticmethod
    def to_numpy_shape(buffer_type: "BufferType") -> tuple:
        if buffer_type == BufferType.vec2:
            return (2,)
        elif buffer_type == BufferType.vec3:
            return (3,)
        elif buffer_type == BufferType.vec4:
            return (4,)
        elif buffer_type == BufferType.rgba8:
            return (4,)
        else:
            return (1,)


if __name__ == "__main__":
    buffer_type = BufferType.vec3

    print("BufferType:", buffer_type, type(buffer_type))
