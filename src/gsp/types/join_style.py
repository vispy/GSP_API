"""Join style enumeration for line rendering."""

from enum import Enum


class JoinStyle(Enum):
    """Join styles for lines.

    Defines how the corners of line segments are rendered when they meet.
    Based on matplotlib's JoinStyle enum.

    Reference:
        https://matplotlib.org/stable/api/_enums_api.html#matplotlib._enums.JoinStyle

    Attributes:
        MITER: Sharp corner by extending outer edges until they meet.
        BEVEL: Flat corner by connecting outer edges with a straight line.
        ROUND: Rounded corner with a circular arc.
    """

    MITER = "miter"
    BEVEL = "bevel"
    ROUND = "round"
