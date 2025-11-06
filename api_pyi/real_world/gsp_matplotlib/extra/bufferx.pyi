import numpy as np
from gsp.types import Buffer, BufferType

class Bufferx:
    @staticmethod
    def mat4_identity() -> Buffer: ...
    @staticmethod
    def to_numpy(buffer: Buffer) -> np.ndarray: ...
    @staticmethod
    def from_numpy(array_numpy: np.ndarray, bufferType: BufferType) -> Buffer: ...
