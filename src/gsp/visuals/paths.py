from ..core.visual_base import VisualBase
from ..types.transbuf import TransBuf
from ..types.buffer import Buffer
from ..types.group import Groups
from ..types.cap_style import CapStyle
from ..types.join_style import JoinStyle


class Paths(VisualBase):
    __slots__ = ["_positions", "_path_sizes", "_colors", "_line_widths", "_cap_style", "_join_style"]

    def __init__(self, positions: TransBuf, path_sizes: TransBuf, colors: TransBuf, line_widths: TransBuf, cap_style: CapStyle, join_style: JoinStyle) -> None:
        super().__init__()

        self._positions: TransBuf = positions
        self._path_sizes: TransBuf = path_sizes
        self._colors: TransBuf = colors
        self._line_widths: TransBuf = line_widths
        self._cap_style: CapStyle = cap_style
        self._join_style: JoinStyle = join_style
        self.check_attributes()

    # =============================================================================
    # get/set attributes
    # =============================================================================

    def get_positions(self) -> TransBuf:
        return self._positions

    def set_positions(self, positions: TransBuf) -> None:
        self._positions = positions
        self.check_attributes()

    def get_path_sizes(self) -> TransBuf:
        return self._path_sizes

    def set_path_sizes(self, path_sizes: TransBuf) -> None:
        self._path_sizes = path_sizes
        self.check_attributes()

    def get_colors(self) -> TransBuf:
        return self._colors

    def set_colors(self, colors: TransBuf) -> None:
        self._colors = colors
        self.check_attributes()

    def get_line_widths(self) -> TransBuf:
        return self._line_widths

    def set_line_widths(self, line_widths: TransBuf) -> None:
        self._line_widths = line_widths
        self.check_attributes()

    def get_join_style(self) -> JoinStyle:
        return self._join_style

    def set_join_style(self, join_style: JoinStyle) -> None:
        self._join_style = join_style
        self.check_attributes()

    def get_cap_style(self) -> CapStyle:
        return self._cap_style

    def set_cap_style(self, cap_style: CapStyle) -> None:
        self._cap_style = cap_style
        self.check_attributes()

    def set_attributes(
        self,
        positions: TransBuf | None = None,
        path_sizes: TransBuf | None = None,
        colors: TransBuf | None = None,
        line_widths: TransBuf | None = None,
        cap_style: CapStyle | None = None,
        join_style: JoinStyle | None = None,
    ) -> None:
        """Set multiple attributes at once and then check their validity."""
        if positions is not None:
            self._positions = positions
        if path_sizes is not None:
            self._path_sizes = path_sizes
        if colors is not None:
            self._colors = colors
        if line_widths is not None:
            self._line_widths = line_widths
        if cap_style is not None:
            self._cap_style = cap_style
        if join_style is not None:
            self._join_style = join_style
        self.check_attributes()

    # =============================================================================
    # Sanity check functions
    # =============================================================================

    def check_attributes(self) -> None:
        """Check that the attributes are valid and consistent."""
        self.sanity_check_attributes(self._positions, self._path_sizes, self._colors, self._line_widths, self._cap_style, self._join_style)

    @staticmethod
    def sanity_check_attributes_buffer(
        positions: Buffer, path_sizes: Buffer, colors: Buffer, line_widths: Buffer, cap_style: CapStyle, join_style: JoinStyle
    ) -> None:
        """same as .sanity_check_attributes() but accept only Buffers.

        - It is meant to be used after converting TransBuf to Buffer.
        """
        # sanity check - each attribute must be a Buffer (not a transform chain)
        assert isinstance(positions, Buffer), "Positions must be a Buffer"
        assert isinstance(path_sizes, Buffer), "Path sizes must be a Buffer"
        assert isinstance(colors, Buffer), "Colors must be a Buffer"
        assert isinstance(line_widths, Buffer), "Line widths must be a Buffer"

        Paths.sanity_check_attributes(positions, path_sizes, colors, line_widths, cap_style, join_style)

    @staticmethod
    def sanity_check_attributes(
        positions: TransBuf,
        path_sizes: TransBuf,
        colors: TransBuf,
        line_widths: TransBuf,
        cap_style: CapStyle,
        join_style: JoinStyle,
    ) -> None:

        pass
