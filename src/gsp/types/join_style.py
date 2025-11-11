from enum import Enum


class JoinStyle(Enum):
    """Join styles for lines. "miter", "bevel", "round"."
    - https://matplotlib.org/stable/api/_enums_api.html#matplotlib._enums.JoinStyle
    """

    MITER = "miter"
    BEVEL = "bevel"
    ROUND = "round"
