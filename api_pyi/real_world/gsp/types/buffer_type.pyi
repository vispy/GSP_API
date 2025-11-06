import numpy as np
from dataclasses import dataclass as dataclass
from enum import Enum

class BufferType(Enum):
    float32 = 0
    uint32 = 1
    uint8 = 2
    int32 = 3
    int8 = 4
    vec2 = 5
    vec3 = 6
    vec4 = 7
    mat4 = 8
    rgba8 = 9
    @staticmethod
    def get_item_size(buffer_type: BufferType) -> int: ...
    @staticmethod
    def to_numpy_dtype(buffer_type: BufferType) -> np.dtype: ...
    @staticmethod
    def from_numpy(ndarray: np.ndarray) -> BufferType: ...
    @staticmethod
    def to_numpy_shape(buffer_type: BufferType) -> tuple: ...
