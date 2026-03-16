"""Text alignment enumeration for text rendering.

Provides a unified text alignment type combining vertical and horizontal alignment
using a compact encoding scheme: value = vertical * 10 + horizontal

This resolves the anchor/alignment bugs by providing a type-safe, backend-agnostic
way to specify text alignment.
"""

from enum import IntEnum


class TextAlign(IntEnum):
    """Combined vertical and horizontal text alignment.

    Encodes both vertical and horizontal alignment into a single integer value
    using the formula: value = vertical * 10 + horizontal

    This allows for compact representation and easy encoding/decoding:
    - Encoding: value = (vertical_index * 10) + horizontal_index
    - Decoding: vertical_index = value // 10, horizontal_index = value % 10

    Attributes:
        TOP_LEFT: Top-left alignment (value 0).
        TOP_CENTER: Top-center alignment (value 1).
        TOP_RIGHT: Top-right alignment (value 2).
        CENTER_LEFT: Center-left alignment (value 10).
        CENTER_CENTER: Center-center alignment (value 11).
        CENTER_RIGHT: Center-right alignment (value 12).
        BOTTOM_LEFT: Bottom-left alignment (value 20).
        BOTTOM_CENTER: Bottom-center alignment (value 21).
        BOTTOM_RIGHT: Bottom-right alignment (value 22).

    Example:
        >>> align = TextAlign.TOP_LEFT
        >>> align.vertical()
        <VerticalAlign.TOP: 0>
        >>> align.horizontal()
        <HorizontalAlign.LEFT: 0>
        >>> TextAlign.from_components(VerticalAlign.CENTER, HorizontalAlign.RIGHT)
        <TextAlign.CENTER_RIGHT: 12>
        >>> TextAlign.from_components(1, 2)  # Also accepts ints
        <TextAlign.CENTER_RIGHT: 12>
    """

    TOP_LEFT = 0
    TOP_CENTER = 1
    TOP_RIGHT = 2
    CENTER_LEFT = 10
    CENTER_CENTER = 11
    CENTER_RIGHT = 12
    BOTTOM_LEFT = 20
    BOTTOM_CENTER = 21
    BOTTOM_RIGHT = 22
