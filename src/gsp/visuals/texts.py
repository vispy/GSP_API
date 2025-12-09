from ..types.visual_base import VisualBase
from ..types.transbuf import TransBuf
from ..types.buffer import Buffer
from ..types.group import Groups
from ..types.cap_style import CapStyle
from ..types.join_style import JoinStyle


class Texts(VisualBase):
    __slots__ = ["_positions", "_texts", "_colors", "_font_sizes", "_anchors", "_angles", "_font_name"]

    def __init__(
        self,
        positions: TransBuf,
        texts: list[str],
        colors: TransBuf,
        font_sizes: TransBuf,
        anchors: TransBuf,
        angles: TransBuf,
        font_name: str,
    ) -> None:
        super().__init__()

        self._positions: TransBuf = positions
        self._texts: list[str] = texts
        self._colors: TransBuf = colors
        self._font_sizes: TransBuf = font_sizes
        self._anchors: TransBuf = anchors
        self._angles: TransBuf = angles
        self._font_name: str = font_name
        self.check_attributes()

    # =============================================================================
    # get/set attributes
    # =============================================================================

    def get_positions(self) -> TransBuf:
        return self._positions

    def set_positions(self, positions: TransBuf) -> None:
        self._positions = positions
        self.check_attributes()

    def get_texts(self) -> list[str]:
        return self._texts

    def set_texts(self, texts: list[str]) -> None:
        self._texts = texts
        self.check_attributes()

    def get_colors(self) -> TransBuf:
        return self._colors

    def set_colors(self, colors: TransBuf) -> None:
        self._colors = colors
        self.check_attributes()

    def get_font_sizes(self) -> TransBuf:
        return self._font_sizes

    def set_font_sizes(self, font_sizes: TransBuf) -> None:
        self._font_sizes = font_sizes
        self.check_attributes()

    def get_anchors(self) -> TransBuf:
        return self._anchors

    def set_anchors(self, anchors: TransBuf) -> None:
        self._anchors = anchors
        self.check_attributes()

    def get_angles(self) -> TransBuf:
        return self._angles

    def set_angles(self, angles: TransBuf) -> None:
        self._angles = angles
        self.check_attributes()

    def get_font_name(self) -> str:
        return self._font_name

    def set_font_name(self, font_name: str) -> None:
        self._font_name = font_name
        self.check_attributes()

    def set_attributes(
        self,
        positions: TransBuf | None = None,
        texts: list[str] | None = None,
        colors: TransBuf | None = None,
        font_sizes: TransBuf | None = None,
        anchors: TransBuf | None = None,
        angles: TransBuf | None = None,
        font_name: str | None = None,
    ) -> None:
        """Set multiple attributes at once and then check their validity."""
        if positions is not None:
            self._positions = positions
        if texts is not None:
            self._texts = texts
        if colors is not None:
            self._colors = colors
        if font_sizes is not None:
            self._font_sizes = font_sizes
        if anchors is not None:
            self._anchors = anchors
        if angles is not None:
            self._angles = angles
        if font_name is not None:
            self._font_name = font_name
        self.check_attributes()

    # =============================================================================
    # Sanity check functions
    # =============================================================================

    def check_attributes(self) -> None:
        """Check that the attributes are valid and consistent."""
        self.sanity_check_attributes(self._positions, self._texts, self._colors, self._font_sizes, self._anchors, self._angles, self._font_name)

    @staticmethod
    def sanity_check_attributes_buffer(
        positions: Buffer, texts: list[str], colors: Buffer, font_sizes: Buffer, anchors: Buffer, angles: Buffer, font_name: str
    ) -> None:
        """same as .sanity_check_attributes() but accept only Buffers.

        - It is meant to be used after converting TransBuf to Buffer.
        """
        # sanity check - each attribute must be a Buffer (not a transform chain)
        assert isinstance(positions, Buffer), "Positions must be a Buffer"
        assert isinstance(texts, list), "Texts must be a list of strings"
        assert isinstance(colors, Buffer), "Colors must be a Buffer"
        assert isinstance(font_sizes, Buffer), "Font sizes must be a Buffer"
        assert isinstance(anchors, Buffer), "Anchors must be a Buffer"
        assert isinstance(angles, Buffer), "Angles must be a Buffer"
        assert isinstance(font_name, str), "Font name must be a string"

        Texts.sanity_check_attributes(positions, texts, colors, font_sizes, anchors, angles, font_name)

    @staticmethod
    def sanity_check_attributes(
        positions: TransBuf,
        texts: list[str],
        colors: TransBuf,
        font_sizes: TransBuf,
        anchors: TransBuf,
        angles: TransBuf,
        font_name: str,
    ) -> None:

        pass
