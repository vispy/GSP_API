from .types.buffer import Buffer
from .types.buffer_type import BufferType


class Constants:
    """Common constants in GSP. e.g. colors."""

    class Color:
        """
        Common colors as RGBA bytearrays. Each color is represented as a bytearray of four integers
        corresponding to the red, green, blue, and alpha (opacity) channels, respectively.
        Each channel value ranges from 0 to 255.
        """

        white = bytearray([255, 255, 255, 255])
        black = bytearray([0, 0, 0, 255])
        red = bytearray([255, 0, 0, 255])
        green = bytearray([0, 255, 0, 255])
        blue = bytearray([0, 0, 255, 255])

        yellow = bytearray([255, 255, 0, 255])
        magenta = bytearray([255, 0, 255, 255])
        cyan = bytearray([0, 255, 255, 255])

        transparent = bytearray([0, 0, 0, 0])
