"""Utility class for converting GSP types to Matplotlib types."""

# stdlib imports
from typing import Literal

# local imports
from gsp.types import CapStyle, JoinStyle, MarkerShape


class ConverterUtils:
    """Utility class for converting GSP types to Matplotlib types."""

    @staticmethod
    def cap_style_gsp_to_mpl(gsp_cap_style: CapStyle) -> Literal["butt", "round", "projecting"]:
        """Convert CapStyle enum to Matplotlib string.

        Args:
            gsp_cap_style (CapStyle): The GSP cap style.

        Returns:
            str: The corresponding Matplotlib cap style.
        """
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
        """Convert JoinStyle enum to Matplotlib string.

        Args:
            gsp_join_style (JoinStyle): The GSP join style.

        Returns:
            str: The corresponding Matplotlib join style.
        """
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
        """Convert GSP marker shape to Matplotlib marker shape.

        - https://matplotlib.org/stable/api/markers_api.html

        Args:
            gsp_marker_shape (MarkerShape): The GSP marker shape.

        Returns:
            str: The corresponding Matplotlib marker shape.
        """
        if gsp_marker_shape == MarkerShape.disc:
            return "o"
            # return "X"
        elif gsp_marker_shape == MarkerShape.asterisk:
            return "*"
        elif gsp_marker_shape == MarkerShape.square:
            return "s"
        elif gsp_marker_shape == MarkerShape.triangle_down:
            return "v"
        elif gsp_marker_shape == MarkerShape.triangle_up:
            return "^"
        elif gsp_marker_shape == MarkerShape.triangle_left:
            return "<"
        elif gsp_marker_shape == MarkerShape.triangle_right:
            return ">"
        elif gsp_marker_shape == MarkerShape.cross:
            return "X"
        elif gsp_marker_shape == MarkerShape.club:
            return r"$\clubsuit$"
        elif gsp_marker_shape == MarkerShape.diamond:
            return "D"
        elif gsp_marker_shape == MarkerShape.heart:
            return r"$\heartsuit$"
        elif gsp_marker_shape == MarkerShape.spade:
            return r"$\spadesuit$"
        elif gsp_marker_shape == MarkerShape.vbar:
            return "|"
        elif gsp_marker_shape == MarkerShape.hbar:
            return "_"
        else:
            raise ValueError(f"Unsupported marker shape: {gsp_marker_shape}")
