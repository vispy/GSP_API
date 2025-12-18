"""Points visual module."""

from ..types.visual_base import VisualBase
from ..types.transbuf import TransBuf
from ..types.buffer import Buffer
from ..types.group import Groups


class Points(VisualBase):
    """Points visual for rendering point markers.
    
    This visual represents a collection of points with configurable positions,
    sizes, face colors, edge colors, and edge widths.
    """
    __slots__ = ["_positions", "_sizes", "_face_colors", "_edge_colors", "_edge_widths"]

    def __init__(self, positions: TransBuf, sizes: TransBuf, face_colors: TransBuf, edge_colors: TransBuf, edge_widths: TransBuf):
        """Initialize Points visual.
        
        Args:
            positions: Positions of the points.
            sizes: Sizes of the points.
            face_colors: Face colors of the points.
            edge_colors: Edge colors of the points.
            edge_widths: Edge widths of the points.
        """
        super().__init__()

        self._positions: TransBuf = positions
        self._sizes: TransBuf = sizes
        self._face_colors: TransBuf = face_colors
        self._edge_colors: TransBuf = edge_colors
        self._edge_widths: TransBuf = edge_widths

        self.check_attributes()

    # =============================================================================
    # get/set attributes
    # =============================================================================

    def get_positions(self) -> TransBuf:
        """Get positions of the points."""
        return self._positions

    def set_positions(self, positions: TransBuf) -> None:
        """Set positions of the points.
        
        Args:
            positions: New positions for the points.
        """
        self._positions = positions
        self.check_attributes()

    def get_sizes(self) -> TransBuf:
        """Get sizes of the points."""
        return self._sizes

    def set_sizes(self, sizes: TransBuf) -> None:
        """Set sizes of the points.
        
        Args:
            sizes: New sizes for the points.
        """
        self._sizes = sizes
        self.check_attributes()

    def get_face_colors(self) -> TransBuf:
        """Get face colors of the points."""
        return self._face_colors

    def set_face_colors(self, face_colors: TransBuf) -> None:
        """Set face colors of the points.
        
        Args:
            face_colors: New face colors for the points.
        """
        self._face_colors = face_colors
        self.check_attributes()

    def get_edge_colors(self) -> TransBuf:
        """Get edge colors of the points."""
        return self._edge_colors

    def set_edge_colors(self, edge_colors: TransBuf) -> None:
        """Set edge colors of the points.
        
        Args:
            edge_colors: New edge colors for the points.
        """
        self._edge_colors = edge_colors
        self.check_attributes()

    def get_edge_widths(self) -> TransBuf:
        """Get edge widths of the points."""
        return self._edge_widths

    def set_edge_widths(self, edge_widths: TransBuf) -> None:
        """Set edge widths of the points.
        
        Args:
            edge_widths: New edge widths for the points.
        """
        self._edge_widths = edge_widths
        self.check_attributes()

    def set_attributes(
        self,
        positions: TransBuf | None = None,
        sizes: TransBuf | None = None,
        face_colors: TransBuf | None = None,
        edge_colors: TransBuf | None = None,
        edge_widths: TransBuf | None = None,
    ) -> None:
        """Set multiple attributes at once and then check their validity."""
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
        self.sanity_check_attributes(self._positions, self._sizes, self._face_colors, self._edge_colors, self._edge_widths)

    @staticmethod
    def sanity_check_attributes_buffer(positions: Buffer, sizes: Buffer, face_colors: Buffer, edge_colors: Buffer, edge_widths: Buffer):
        """Same as .sanity_check_attributes() but accept only Buffers.

        - It is meant to be used after converting TransBuf to Buffer.
        """
        # sanity check - each attribute must be a Buffer (not a transform chain)
        assert isinstance(positions, Buffer), "Positions must be a Buffer"
        assert isinstance(sizes, Buffer), "Sizes must be a Buffer"
        assert isinstance(face_colors, Buffer), "Face colors must be a Buffer"
        assert isinstance(edge_colors, Buffer), "Edge colors must be a Buffer"
        assert isinstance(edge_widths, Buffer), "Edge widths must be a Buffer"

        Points.sanity_check_attributes(positions, sizes, face_colors, edge_colors, edge_widths)

    @staticmethod
    def sanity_check_attributes(
        positions: TransBuf,
        sizes: TransBuf,
        face_colors: TransBuf,
        edge_colors: TransBuf,
        edge_widths: TransBuf,
    ) -> None:
        """Check that the attributes are valid and consistent.
        
        Args:
            positions: Positions of the points.
            sizes: Sizes of the points.
            face_colors: Face colors of the points.
            edge_colors: Edge colors of the points.
            edge_widths: Edge widths of the points.
        """
        pass
