# stdlib imports
import typing
from typing import Literal

# local imports
from gsp.types import CapStyle, JoinStyle, MarkerShape


class ConverterUtils:
    """Utility class for converting GSP types to Matplotlib types."""

    @staticmethod
    def cap_style_gsp_to_mpl(gsp_cap_style: CapStyle) -> Literal["butt", "round", "projecting"]:
        """Convert CapStyle enum to Matplotlib string."""

        if gsp_cap_style == CapStyle.BUTT:
            return "butt"
        elif gsp_cap_style == CapStyle.ROUND:
            return "round"
        elif gsp_cap_style == CapStyle.PROJECTING:
            return "projecting"
        else:
            raise ValueError(f"Unsupported CapStyle: {gsp_cap_style}")

    @staticmethod
    def join_style_gsp_to_mpl(gsp_join_style: JoinStyle) -> Literal["miter", "round", "bevel"]:
        """Convert JoinStyle enum to Matplotlib string."""
        if gsp_join_style == JoinStyle.MITER:
            return "miter"
        elif gsp_join_style == JoinStyle.ROUND:
            return "round"
        elif gsp_join_style == JoinStyle.BEVEL:
            return "bevel"
        else:
            raise ValueError(f"Unsupported JoinStyle: {gsp_join_style}")

    @staticmethod
    def marker_shape_gsp_to_mpl(gsp_marker_shape: MarkerShape) -> str:
        """Convert GSP marker shape to Matplotlib marker shape."""

        if gsp_marker_shape == MarkerShape.disc:
            mpl_marker_shape = "o"
        elif gsp_marker_shape == MarkerShape.square:
            mpl_marker_shape = "s"
        elif gsp_marker_shape == MarkerShape.club:
            mpl_marker_shape = r"$\clubsuit$"
        else:
            raise ValueError(f"Unsupported marker shape: {gsp_marker_shape}")

        return mpl_marker_shape
