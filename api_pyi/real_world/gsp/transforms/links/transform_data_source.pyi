from ...types.buffer import Buffer as Buffer
from ...types.buffer_type import BufferType as BufferType
from ..transform_link import TransformLink as TransformLink

class TransformDataSource(TransformLink):
    def __init__(self, uri: str, buffer_type: BufferType) -> None: ...
    def apply(self, buffer_src: Buffer | None) -> Buffer: ...
