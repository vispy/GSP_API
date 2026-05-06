"""Common constants for GSP including color definitions."""

# stdlib imports
from enum import Enum

# local imports
from .types.color import Color


class Constants:
    """Common constants in GSP. e.g. colors."""

    class FaceCulling(Enum):
        FrontSide = 0
        BackSide = 1
        BothSides = 2

    class Color:
        """Common colors as RGBA bytearrays.

        Each color is represented as a bytearray of four integers
        corresponding to the red, green, blue, and alpha (opacity) channels, respectively.
        Each channel value ranges from 0 to 255.
        """

        white: Color = bytearray([255, 255, 255, 255])
        black: Color = bytearray([0, 0, 0, 255])
        red: Color = bytearray([255, 0, 0, 255])
        green: Color = bytearray([0, 255, 0, 255])
        blue: Color = bytearray([0, 0, 255, 255])

        yellow: Color = bytearray([255, 255, 0, 255])
        magenta: Color = bytearray([255, 0, 255, 255])
        cyan: Color = bytearray([0, 255, 255, 255])

        light_gray: Color = bytearray([211, 211, 211, 255])
        gray: Color = bytearray([128, 128, 128, 255])
        dark_gray: Color = bytearray([64, 64, 64, 255])

        transparent: Color = bytearray([0, 0, 0, 0])
