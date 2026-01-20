"""Cap style enumeration for line rendering."""

from enum import Enum


class ImageInterpolation(Enum):
    """Interpolation for Image.

    Defines the style of line caps: "linear" or "nearest".
    """

    LINEAR = "linear"
    NEAREST = "nearest"
