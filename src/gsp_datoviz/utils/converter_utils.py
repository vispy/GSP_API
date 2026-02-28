"""Utility functions for converting GSP types to Datoviz types."""

# stdlib imports
import math

# local imports
from gsp.types import CapStyle, JoinStyle
from gsp.types import MarkerShape


class ConverterUtils:
    """Utility class for converting GSP types to Datoviz types."""

    @staticmethod
    def cap_style_gsp_to_dvz(cap_style: CapStyle) -> str:
        """Convert CapStyle enum to Datoviz string.

        Args:
            cap_style: The GSP CapStyle enum value.

        Returns:
            The corresponding Datoviz cap style string.
        """
        if cap_style == CapStyle.BUTT:
            return "butt"
        elif cap_style == CapStyle.ROUND:
            return "round"
        elif cap_style == CapStyle.PROJECTING:
            return "square"
        else:
            raise ValueError(f"Unsupported CapStyle: {cap_style}")

    @staticmethod
    def join_style_gsp_to_dvz(join_style: JoinStyle) -> str:
        """Convert JoinStyle enum to Datoviz string.

        Args:
            join_style: The GSP JoinStyle enum value.

        Returns:
            The corresponding Datoviz join style string.
        """
        if join_style == JoinStyle.MITER:
            raise ValueError(f"Unsupported JoinStyle in datoviz: {join_style}")
        elif join_style == JoinStyle.ROUND:
            return "round"
        elif join_style == JoinStyle.BEVEL:
            return "square"
        else:
            raise ValueError(f"Unsupported JoinStyle: {join_style}")

    @staticmethod
    def marker_shape_gsp_to_dvz(gsp_marker_shape: MarkerShape) -> tuple[str, float]:
        """Convert GSP marker shape to Datoviz marker shape.

        - https://datoviz.org/visuals/marker/#code

        Args:
            gsp_marker_shape: The GSP MarkerShape enum value.

        Returns:
            The corresponding Datoviz marker shape string and angle (between 0, 2 * np.pi).
        """
        if gsp_marker_shape == MarkerShape.disc:
            return "disc", 0.0
            # return "cross", 0.0
        elif gsp_marker_shape == MarkerShape.asterisk:
            return "asterisk", 0.0
        elif gsp_marker_shape == MarkerShape.triangle_down:
            return "triangle", math.pi
        elif gsp_marker_shape == MarkerShape.triangle_up:
            return "triangle", 0
        elif gsp_marker_shape == MarkerShape.triangle_left:
            return "triangle", math.pi / 2
        elif gsp_marker_shape == MarkerShape.triangle_right:
            return "triangle", -math.pi / 2
        elif gsp_marker_shape == MarkerShape.square:
            return "square", 0
        elif gsp_marker_shape == MarkerShape.cross:
            return "cross", 0.0
        elif gsp_marker_shape == MarkerShape.club:
            return "club", 0.0
        elif gsp_marker_shape == MarkerShape.diamond:
            return "diamond", 0.0
        elif gsp_marker_shape == MarkerShape.heart:
            return "heart", 0.0
        elif gsp_marker_shape == MarkerShape.spade:
            return "spade", 0.0
        elif gsp_marker_shape == MarkerShape.vbar:
            return "vbar", 0.0
        elif gsp_marker_shape == MarkerShape.hbar:
            return "hbar", 0.0
        else:
            raise ValueError(f"Unsupported marker shape: {gsp_marker_shape}")
