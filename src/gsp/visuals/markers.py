from ..types.visual_base import VisualBase
from ..types.transbuf import TransBuf
from ..types.buffer import Buffer
from ..types.group import Groups
from ..types.marker_shape import MarkerShape


class Markers(VisualBase):
    __slots__ = ["_marker_shape", "_positions", "_sizes", "_face_colors", "_edge_colors", "_edge_widths"]

    def __init__(self, marker_shape: MarkerShape, positions: TransBuf, sizes: TransBuf, face_colors: TransBuf, edge_colors: TransBuf, edge_widths: TransBuf):
        super().__init__()

        self._marker_shape: MarkerShape = marker_shape
        self._positions: TransBuf = positions
        self._sizes: TransBuf = sizes
        self._face_colors: TransBuf = face_colors
        self._edge_colors: TransBuf = edge_colors
        self._edge_widths: TransBuf = edge_widths

        self.check_attributes()

    # =============================================================================
    # get/set attributes
    # =============================================================================

    def get_marker_shape(self) -> MarkerShape:
        return self._marker_shape

    def set_marker_shape(self, marker_shape: MarkerShape) -> None:
        self._marker_shape = marker_shape
        self.check_attributes()

    def get_positions(self) -> TransBuf:
        return self._positions

    def set_positions(self, positions: TransBuf) -> None:
        self._positions = positions
        self.check_attributes()

    def get_sizes(self) -> TransBuf:
        return self._sizes

    def set_sizes(self, sizes: TransBuf) -> None:
        self._sizes = sizes
        self.check_attributes()

    def get_face_colors(self) -> TransBuf:
        return self._face_colors

    def set_face_colors(self, face_colors: TransBuf) -> None:
        self._face_colors = face_colors
        self.check_attributes()

    def get_edge_colors(self) -> TransBuf:
        return self._edge_colors

    def set_edge_colors(self, edge_colors: TransBuf) -> None:
        self._edge_colors = edge_colors
        self.check_attributes()

    def get_edge_widths(self) -> TransBuf:
        return self._edge_widths

    def set_edge_widths(self, edge_widths: TransBuf) -> None:
        self._edge_widths = edge_widths
        self.check_attributes()

    def set_attributes(
        self,
        marker_shape: MarkerShape | None = None,
        positions: TransBuf | None = None,
        sizes: TransBuf | None = None,
        face_colors: TransBuf | None = None,
        edge_colors: TransBuf | None = None,
        edge_widths: TransBuf | None = None,
    ) -> None:
        """Set multiple attributes at once and then check their validity."""
        if marker_shape is not None:
            self._marker_shape = marker_shape
        if positions is not None:
            self._positions = positions
        if sizes is not None:
            self._sizes = sizes
        if face_colors is not None:
            self._face_colors = face_colors
        if edge_colors is not None:
            self._edge_colors = edge_colors
        if edge_widths is not None:
            self._edge_widths = edge_widths
        self.check_attributes()

    # =============================================================================
    # Sanity check functions
    # =============================================================================

    def check_attributes(self) -> None:
        """Check that the attributes are valid and consistent."""
        self.sanity_check_attributes(self._marker_shape, self._positions, self._sizes, self._face_colors, self._edge_colors, self._edge_widths)

    @staticmethod
    def sanity_check_attributes_buffer(
        marker_shape: MarkerShape, positions: Buffer, sizes: Buffer, face_colors: Buffer, edge_colors: Buffer, edge_widths: Buffer
    ):
        """same as .sanity_check_attributes() but accept only Buffers.

        - It is meant to be used after converting TransBuf to Buffer.
        """
        # sanity check - each attribute must be a Buffer (not a transform chain)
        assert isinstance(positions, Buffer), "Positions must be a Buffer"
        assert isinstance(sizes, Buffer), "Sizes must be a Buffer"
        assert isinstance(face_colors, Buffer), "Face colors must be a Buffer"
        assert isinstance(edge_colors, Buffer), "Edge colors must be a Buffer"
        assert isinstance(edge_widths, Buffer), "Edge widths must be a Buffer"

        Markers.sanity_check_attributes(marker_shape, positions, sizes, face_colors, edge_colors, edge_widths)

    @staticmethod
    def sanity_check_attributes(
        marker_shape: MarkerShape,
        positions: TransBuf,
        sizes: TransBuf,
        face_colors: TransBuf,
        edge_colors: TransBuf,
        edge_widths: TransBuf,
    ) -> None:

        pass
