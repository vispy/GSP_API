"""Texts visual module."""

from ..types.visual_base import VisualBase
from ..types.transbuf import TransBuf
from ..types.buffer import Buffer


class Texts(VisualBase):
    """Texts visual."""

    __slots__ = ["_positions", "_strings", "_colors", "_font_sizes", "_anchors", "_angles", "_font_name"]

    def __init__(
        self,
        positions: TransBuf,
        strings: list[str],
        colors: TransBuf,
        font_sizes: TransBuf,
        anchors: TransBuf,
        angles: TransBuf,
        font_name: str,
    ) -> None:
        """Initialize Texts visual.

        Args:
            positions (TransBuf): Positions of the texts.
            strings (list[str]): List of text strings.
            colors (TransBuf): Colors of the texts.
            font_sizes (TransBuf): Font sizes of the texts.
            anchors (TransBuf): Anchor positions of the texts.
            angles (TransBuf): Rotation angles of the texts.
            font_name (str): Font name for the texts.
        """
        super().__init__()

        self._positions: TransBuf = positions
        self._strings: list[str] = strings
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
        """Get positions of the texts."""
        return self._positions

    def set_positions(self, positions: TransBuf) -> None:
        """Set positions of the texts.

        Args:
            positions: New positions for the texts.
        """
        self._positions = positions
        self.check_attributes()

    def get_strings(self) -> list[str]:
        """Get text strings."""
        return self._strings

    def set_strings(self, strings: list[str]) -> None:
        """Set text strings.

        Args:
            strings: New text strings.
        """
        self._strings = strings
        self.check_attributes()

    def get_colors(self) -> TransBuf:
        """Get colors of the texts."""
        return self._colors

    def set_colors(self, colors: TransBuf) -> None:
        """Set colors of the texts.

        Args:
            colors: New colors for the texts.
        """
        self._colors = colors
        self.check_attributes()

    def get_font_sizes(self) -> TransBuf:
        """Get font sizes of the texts."""
        return self._font_sizes

    def set_font_sizes(self, font_sizes: TransBuf) -> None:
        """Set font sizes of the texts.

        Args:
            font_sizes: New font sizes for the texts.
        """
        self._font_sizes = font_sizes
        self.check_attributes()

    def get_anchors(self) -> TransBuf:
        """Get anchor positions of the texts."""
        return self._anchors

    def set_anchors(self, anchors: TransBuf) -> None:
        """Set anchor positions of the texts.

        Args:
            anchors: New anchor positions for the texts.
        """
        self._anchors = anchors
        self.check_attributes()

    def get_angles(self) -> TransBuf:
        """Get rotation angles of the texts."""
        return self._angles

    def set_angles(self, angles: TransBuf) -> None:
        """Set rotation angles of the texts.

        Args:
            angles: New rotation angles for the texts.
        """
        self._angles = angles
        self.check_attributes()

    def get_font_name(self) -> str:
        """Get font name used for the texts."""
        return self._font_name

    def set_font_name(self, font_name: str) -> None:
        """Set font name for the texts.

        Args:
            font_name: New font name for the texts.
        """
        self._font_name = font_name
        self.check_attributes()

    def set_attributes(
        self,
        positions: TransBuf | None = None,
        strings: list[str] | None = None,
        colors: TransBuf | None = None,
        font_sizes: TransBuf | None = None,
        anchors: TransBuf | None = None,
        angles: TransBuf | None = None,
        font_name: str | None = None,
    ) -> None:
        """Set multiple attributes at once and then check their validity."""
        if positions is not None:
            self._positions = positions
        if strings is not None:
            self._strings = strings
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
        self.sanity_check_attributes(self._positions, self._strings, self._colors, self._font_sizes, self._anchors, self._angles, self._font_name)

    @staticmethod
    def sanity_check_attributes_buffer(
        positions: Buffer, strings: list[str], colors: Buffer, font_sizes: Buffer, anchors: Buffer, angles: Buffer, font_name: str
    ) -> None:
        """Same as .sanity_check_attributes() but accept only Buffers.

        - It is meant to be used after converting TransBuf to Buffer.
        """
        # sanity check - each attribute must be a Buffer (not a transform chain)
        assert isinstance(positions, Buffer), "Positions must be a Buffer"
        assert isinstance(strings, list), "Texts must be a list of strings"
        assert isinstance(colors, Buffer), "Colors must be a Buffer"
        assert isinstance(font_sizes, Buffer), "Font sizes must be a Buffer"
        assert isinstance(anchors, Buffer), "Anchors must be a Buffer"
        assert isinstance(angles, Buffer), "Angles must be a Buffer"
        assert isinstance(font_name, str), "Font name must be a string"

        # check positions, colors, font_sizes, anchors, angles have the same length as strings
        assert positions.get_count() == len(
            strings
        ), f"Positions length must match number of strings. Got {positions.get_count()} positions vs {len(strings)} strings"
        assert colors.get_count() == len(strings), f"Colors length must match number of strings. Got {colors.get_count()} colors vs {len(strings)} strings"
        assert font_sizes.get_count() == len(
            strings
        ), f"Font sizes length must match number of strings. Got {font_sizes.get_count()} font sizes vs {len(strings)} strings"
        assert anchors.get_count() == len(strings), f"Anchors length must match number of strings. Got {anchors.get_count()} anchors vs {len(strings)} strings"
        assert angles.get_count() == len(strings), f"Angles length must match number of strings. Got {angles.get_count()} angles vs {len(strings)} strings"

        # check font_name is not empty and is a string
        assert len(font_name) > 0, "Font name must be a non-empty string"
        assert isinstance(font_name, str), "Font name must be a string"

        # check all strings are indeed strings
        for string in strings:
            assert isinstance(string, str), "All elements in strings must be of type str"

    @staticmethod
    def sanity_check_attributes(
        positions: TransBuf,
        strings: list[str],
        colors: TransBuf,
        font_sizes: TransBuf,
        anchors: TransBuf,
        angles: TransBuf,
        font_name: str,
    ) -> None:
        """Check that the attributes are valid and consistent.

        Args:
            positions: Positions of the texts.
            strings: List of text strings.
            colors: Colors of the texts.
            font_sizes: Font sizes of the texts.
            anchors: Anchor positions of the texts.
            angles: Rotation angles of the texts.
            font_name: Font name for the texts.
        """
        pass
