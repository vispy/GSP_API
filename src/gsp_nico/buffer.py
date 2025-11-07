# stdlib imports
import numpy as np

# local imports
from gsp.types import Buffer as GspBuffer
from gsp.types import BufferType as GspBufferType
from gsp_matplotlib.extra import Bufferx as GspBufferx


class Buffer:
    @staticmethod
    def from_numpy(array: np.ndarray, dtype: str) -> GspBuffer:
        # Implementation to create a Buffer from a numpy array
        buftype = Buffer._strtype_to_buftype(dtype)
        gsp_buffer = GspBufferx.from_numpy(array, buftype)
        return gsp_buffer

    @staticmethod
    def from_bytes(byte_data: bytearray, dtype: str) -> GspBuffer:
        buffer_type = Buffer._strtype_to_buftype(dtype)
        gsp_buffer = GspBuffer.from_bytearray(byte_data, buffer_type)
        return gsp_buffer

    @staticmethod
    def _strtype_to_buftype(strtype: str) -> GspBufferType:
        if strtype == "float32":
            return GspBufferType.float32
        elif strtype == "uint32":
            return GspBufferType.uint32
        elif strtype == "uint8":
            return GspBufferType.uint8
        elif strtype == "int32":
            return GspBufferType.int32
        elif strtype == "int8":
            return GspBufferType.int8
        elif strtype == "vec2":
            return GspBufferType.vec2
        elif strtype == "vec3":
            return GspBufferType.vec3
        elif strtype == "vec4":
            return GspBufferType.vec4
        elif strtype == "uvec4":
            return GspBufferType.uvec4
        elif strtype == "mat4":
            return GspBufferType.mat4
        elif strtype == "rgba8":
            return GspBufferType.rgba8
        else:
            raise ValueError(f"Unknown buffer type string: {strtype}")
