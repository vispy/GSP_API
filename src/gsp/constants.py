from .types.buffer import Buffer
from .types.buffer_type import BufferType


class Constants:
    """Common constants like colors."""

    class Colors:
        """Common colors as RGBA bytearrays."""

        white = bytearray([255, 255, 255, 255])
        black = bytearray([0, 0, 0, 255])
        red = bytearray([255, 0, 0, 255])
        green = bytearray([0, 255, 0, 255])
        blue = bytearray([0, 0, 255, 255])

        yellow = bytearray([255, 255, 0, 255])
        magenta = bytearray([255, 0, 255, 255])
        cyan = bytearray([0, 255, 255, 255])

    class Marker_Shape:
        """Common marker shapes."""

        disc = "disc"
        square = "square"
