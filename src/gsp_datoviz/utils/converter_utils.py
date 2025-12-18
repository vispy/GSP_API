"""Utility functions for converting GSP types to Datoviz types."""

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
    def marker_shape_gsp_to_dvz(gsp_marker_shape: MarkerShape) -> str:
        """Convert GSP marker shape to Datoviz marker shape.
        
        Args:
            gsp_marker_shape: The GSP MarkerShape enum value.
        
        Returns:
            The corresponding Datoviz marker shape string.
        """
        if gsp_marker_shape == MarkerShape.disc:
            mpl_marker_shape = "disc"
        elif gsp_marker_shape == MarkerShape.square:
            mpl_marker_shape = "square"
        elif gsp_marker_shape == MarkerShape.club:
            mpl_marker_shape = "club"
        else:
            raise ValueError(f"Unsupported marker shape: {gsp_marker_shape}")

        return mpl_marker_shape
