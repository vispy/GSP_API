"""Marker visual for rendering 2D/3D markers with customizable shapes, sizes, and colors."""

from ..types.visual_base import VisualBase
from ..types.transbuf import TransBuf
from ..types.buffer import Buffer
from ..types.group import Groups
from ..types.marker_shape import MarkerShape


class Markers(VisualBase):
    """Visual representation of markers with configurable properties.

    This class manages marker visualization with properties including shape,
    positions, sizes, face colors, edge colors, and edge widths.

    Attributes:
        _marker_shape (MarkerShape): The shape of the markers.
        _positions (TransBuf): The positions of the markers.
        _sizes (TransBuf): The sizes of the markers.
        _face_colors (TransBuf): The face colors of the markers.
        _edge_colors (TransBuf): The edge colors of the markers.
        _edge_widths (TransBuf): The edge widths of the markers.
    """
    __slots__ = ["_marker_shape", "_positions", "_sizes", "_face_colors", "_edge_colors", "_edge_widths"]

    def __init__(self, marker_shape: MarkerShape, positions: TransBuf, sizes: TransBuf, face_colors: TransBuf, edge_colors: TransBuf, edge_widths: TransBuf):
        """Initialize a Markers visual.

        Args:
            marker_shape (MarkerShape): The shape of the markers.
            positions (TransBuf): The positions of the markers.
            sizes (TransBuf): The sizes of the markers.
            face_colors (TransBuf): The face colors of the markers.
            edge_colors (TransBuf): The edge colors of the markers.
            edge_widths (TransBuf): The edge widths of the markers.
        """
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
        """Get the marker shape.

        Returns:
            MarkerShape: The marker shape.
        """
        return self._marker_shape

    def set_marker_shape(self, marker_shape: MarkerShape) -> None:
        """Set the marker shape.

        Args:
            marker_shape (MarkerShape): The new marker shape.
        """
        self._marker_shape = marker_shape
        self.check_attributes()

    def get_positions(self) -> TransBuf:
        """Get the marker positions.

        Returns:
            TransBuf: The marker positions.
        """
        return self._positions

    def set_positions(self, positions: TransBuf) -> None:
        """Set the marker positions.

        Args:
            positions (TransBuf): The new marker positions.
        """
        self._positions = positions
        self.check_attributes()

    def get_sizes(self) -> TransBuf:
        """Get the marker sizes.

        Returns:
            TransBuf: The marker sizes.
        """
        return self._sizes

    def set_sizes(self, sizes: TransBuf) -> None:
        """Set the marker sizes.

        Args:
            sizes (TransBuf): The new marker sizes.
        """
        self._sizes = sizes
        self.check_attributes()

    def get_face_colors(self) -> TransBuf:
        """Get the marker face colors.

        Returns:
            TransBuf: The marker face colors.
        """
        return self._face_colors

    def set_face_colors(self, face_colors: TransBuf) -> None:
        """Set the marker face colors.

        Args:
            face_colors (TransBuf): The new marker face colors.
        """
        self._face_colors = face_colors
        self.check_attributes()

    def get_edge_colors(self) -> TransBuf:
        """Get the marker edge colors.

        Returns:
            TransBuf: The marker edge colors.
        """
        return self._edge_colors

    def set_edge_colors(self, edge_colors: TransBuf) -> None:
        """Set the marker edge colors.

        Args:
            edge_colors (TransBuf): The new marker edge colors.
        """
        self._edge_colors = edge_colors
        self.check_attributes()

    def get_edge_widths(self) -> TransBuf:
        """Get the marker edge widths.

        Returns:
            TransBuf: The marker edge widths.
        """
        return self._edge_widths

    def set_edge_widths(self, edge_widths: TransBuf) -> None:
        """Set the marker edge widths.

        Args:
            edge_widths (TransBuf): The new marker edge widths.
        """
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
        """Same as .sanity_check_attributes() but accept only Buffers.

        This method is meant to be used after converting TransBuf to Buffer.

        Args:
            marker_shape (MarkerShape): The marker shape.
            positions (Buffer): The marker positions as a Buffer.
            sizes (Buffer): The marker sizes as a Buffer.
            face_colors (Buffer): The marker face colors as a Buffer.
            edge_colors (Buffer): The marker edge colors as a Buffer.
            edge_widths (Buffer): The marker edge widths as a Buffer.
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
        """Check that the marker attributes are valid and consistent.

        Args:
            marker_shape (MarkerShape): The marker shape.
            positions (TransBuf): The marker positions.
            sizes (TransBuf): The marker sizes.
            face_colors (TransBuf): The marker face colors.
            edge_colors (TransBuf): The marker edge colors.
            edge_widths (TransBuf): The marker edge widths.
        """
        pass
