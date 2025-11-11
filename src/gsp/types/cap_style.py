from enum import Enum


class CapStyle(Enum):
    """
    Cap styles for lines. "butt", "projecting", "round"
    - https://matplotlib.org/stable/api/_enums_api.html#matplotlib._enums.CapStyle
    """

    BUTT = "butt"
    PROJECTING = "projecting"
    ROUND = "round"
