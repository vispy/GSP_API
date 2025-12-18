"""Cap style enumeration for line rendering."""

from enum import Enum


class CapStyle(Enum):
    """Cap styles for lines.

    Defines the style of line caps: "butt", "projecting", or "round".

    Attributes:
        BUTT: Lines end exactly at the endpoint.
        PROJECTING: Lines extend beyond the endpoint by half the line width.
        ROUND: Lines end with a rounded cap.

    Note:
        Based on matplotlib's CapStyle enum.
        See: https://matplotlib.org/stable/api/_enums_api.html#matplotlib._enums.CapStyle
    """

    BUTT = "butt"
    PROJECTING = "projecting"
    ROUND = "round"
