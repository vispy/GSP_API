from gsp.types import CapStyle, JoinStyle


class ConverterUtils:
    @staticmethod
    def cap_style_gsp_to_dvz(cap_style: CapStyle) -> str:
        """Convert CapStyle enum to Matplotlib string."""

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
        """Convert JoinStyle enum to Matplotlib string."""
        if join_style == JoinStyle.MITER:
            raise ValueError(f"Unsupported JoinStyle in datoviz: {join_style}")
        elif join_style == JoinStyle.ROUND:
            return "round"
        elif join_style == JoinStyle.BEVEL:
            return "square"
        else:
            raise ValueError(f"Unsupported JoinStyle: {join_style}")
