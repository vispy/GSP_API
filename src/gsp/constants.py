from .types.buffer import Buffer
from .types.buffer_type import BufferType


class Constants:
    """Common constants like colors."""

    white = bytearray([255, 255, 255, 255])
    black = bytearray([0, 0, 0, 255])
    red = bytearray([255, 0, 0, 255])
    green = bytearray([0, 255, 0, 255])
    blue = bytearray([0, 0, 255, 255])
