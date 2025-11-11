# stdlib imports
import typing
from typing import Literal

# local imports
from gsp.types import CapStyle, JoinStyle


class ConverterUtils:
    @staticmethod
    def cap_style_gsp_to_mpl(cap_style: CapStyle) -> Literal["butt", "round", "projecting"]:
        """Convert CapStyle enum to Matplotlib string."""

        if cap_style == CapStyle.BUTT:
            return "butt"
        elif cap_style == CapStyle.ROUND:
            return "round"
        elif cap_style == CapStyle.PROJECTING:
            return "projecting"
        else:
            raise ValueError(f"Unsupported CapStyle: {cap_style}")

    @staticmethod
    def join_style_gsp_to_mpl(join_style: JoinStyle) -> Literal["miter", "round", "bevel"]:
        """Convert JoinStyle enum to Matplotlib string."""
        if join_style == JoinStyle.MITER:
            return "miter"
        elif join_style == JoinStyle.ROUND:
            return "round"
        elif join_style == JoinStyle.BEVEL:
            return "bevel"
        else:
            raise ValueError(f"Unsupported JoinStyle: {join_style}")
