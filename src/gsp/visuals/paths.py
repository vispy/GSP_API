from ..core.visual_base import VisualBase
from ..types.transbuf import TransBuf
from ..types.buffer import Buffer
from ..types.group import Groups


class Paths(VisualBase):
    __slots__ = (
        "_positions",
        "_path_sizes",
        "_colors",
        "_line_widths",
    )

    def __init__(self, positions: TransBuf, path_sizes: TransBuf, colors: TransBuf, line_widths: TransBuf):
        super().__init__()

        self._positions: TransBuf = positions
        self._path_sizes: TransBuf = path_sizes
        self._colors: TransBuf = colors
        self._line_widths: TransBuf = line_widths

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

    def set_attributes(
        self,
        positions: TransBuf | None = None,
        path_sizes: TransBuf | None = None,
        colors: TransBuf | None = None,
        line_widths: TransBuf | None = None,
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
        self.check_attributes()

    # =============================================================================
    # Sanity check functions
    # =============================================================================

    def check_attributes(self) -> None:
        """Check that the attributes are valid and consistent."""
        self.sanity_check_attributes(self._positions, self._path_sizes, self._colors, self._line_widths)

    @staticmethod
    def sanity_check_attributes_buffer(positions: Buffer, path_sizes: Buffer, colors: Buffer, line_widths: Buffer) -> None:
        """same as .sanity_check_attributes() but accept only Buffers.

        - It is meant to be used after converting TransBuf to Buffer.
        """
        # sanity check - each attribute must be a Buffer (not a transform chain)
        assert isinstance(positions, Buffer), "Positions must be a Buffer"
        assert isinstance(path_sizes, Buffer), "Path sizes must be a Buffer"
        assert isinstance(colors, Buffer), "Colors must be a Buffer"
        assert isinstance(line_widths, Buffer), "Line widths must be a Buffer"

        Paths.sanity_check_attributes(positions, path_sizes, colors, line_widths)

    @staticmethod
    def sanity_check_attributes(
        positions: TransBuf,
        path_sizes: TransBuf,
        colors: TransBuf,
        line_widths: TransBuf,
    ) -> None:

        pass
