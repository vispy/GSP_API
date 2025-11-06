# pip imports
from typing import Literal

# local imports
from gsp.types import BufferType, Buffer
from gsp.transforms.transform_link import TransformLink


class TransformLinkImmediate(TransformLink):
    """A TransformLink that immediately returns a predefined Buffer."""

    def __init__(self, buffer: Buffer) -> None:
        self._buffer = buffer

    def apply(self, buffer_src: Buffer | None) -> Buffer:
        return self._buffer
