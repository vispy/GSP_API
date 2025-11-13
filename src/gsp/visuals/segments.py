from ..core.visual_base import VisualBase
from ..types.transbuf import TransBuf
from ..types.buffer import Buffer
from ..types.group import Groups
from ..types.cap_style import CapStyle
from ..types.join_style import JoinStyle


class Segments(VisualBase):
    __slots__ = (
        "_positions",
        "_colors",
        "_line_widths",
        "_cap_style",
    )

    def __init__(self, positions: TransBuf, line_widths: TransBuf, cap_style: CapStyle, colors: TransBuf) -> None:
        super().__init__()

        self._positions: TransBuf = positions
        self._line_widths: TransBuf = line_widths
        self._cap_style: CapStyle = cap_style
        self._colors: TransBuf = colors

    # =============================================================================
    # get/set attributes
    # =============================================================================

    def get_positions(self) -> TransBuf:
        return self._positions

    def set_positions(self, positions: TransBuf) -> None:
        self._positions = positions
        self.check_attributes()

    def get_line_widths(self) -> TransBuf:
        return self._line_widths

    def set_line_widths(self, line_widths: TransBuf) -> None:
        self._line_widths = line_widths
        self.check_attributes()

    def get_cap_style(self) -> CapStyle:
        return self._cap_style

    def set_cap_style(self, cap_style: CapStyle) -> None:
        self._cap_style = cap_style
        self.check_attributes()

    def get_colors(self) -> TransBuf:
        return self._colors

    def set_colors(self, colors: TransBuf) -> None:
        self._colors = colors
        self.check_attributes()

    def set_attributes(
        self,
        positions: TransBuf | None = None,
        line_widths: TransBuf | None = None,
        cap_style: CapStyle | None = None,
        colors: TransBuf | None = None,
    ) -> None:
        """Set multiple attributes at once and then check their validity."""
        if positions is not None:
            self._positions = positions
        if line_widths is not None:
            self._line_widths = line_widths
        if cap_style is not None:
            self._cap_style = cap_style
        if colors is not None:
            self._colors = colors
        self.check_attributes()

    # =============================================================================
    # Sanity check functions
    # =============================================================================

    def check_attributes(self) -> None:
        """Check that the attributes are valid and consistent."""
        self.sanity_check_attributes(self._positions, self._line_widths, self._cap_style, self._colors)

    @staticmethod
    def sanity_check_attributes_buffer(positions: Buffer, line_widths: Buffer, cap_style: CapStyle, colors: Buffer) -> None:
        """same as .sanity_check_attributes() but accept only Buffers.

        - It is meant to be used after converting TransBuf to Buffer.
        """
        # sanity check - each attribute must be a Buffer (not a transform chain)
        assert isinstance(positions, Buffer), "Positions must be a Buffer"
        assert isinstance(line_widths, Buffer), "Line widths must be a Buffer"
        assert isinstance(colors, Buffer), "Colors must be a Buffer"

        Segments.sanity_check_attributes(positions, line_widths, cap_style, colors)

    @staticmethod
    def sanity_check_attributes(
        positions: TransBuf,
        line_widths: TransBuf,
        cap_style: CapStyle,
        colors: TransBuf,
    ) -> None:

        pass
