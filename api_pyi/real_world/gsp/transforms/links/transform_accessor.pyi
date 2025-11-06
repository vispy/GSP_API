from ...types import Buffer as Buffer, BufferType as BufferType
from ..transform_link import TransformLink as TransformLink
from _typeshed import Incomplete

TransformAccessorFieldName: Incomplete

class TransformAccessor(TransformLink):
    def __init__(self, field_name: TransformAccessorFieldName) -> None: ...
    def apply(self, buffer_src: Buffer | None) -> Buffer: ...
