from ..core.visual_base import VisualBase
from ..types.transbuf import TransBuf
from ..types.buffer import Buffer
from ..types.group import Groups


class Points(VisualBase):
    def __init__(self, positions: TransBuf, sizes: TransBuf, face_colors: TransBuf, edge_colors: TransBuf, edge_widths: TransBuf, groups: Groups):
        super().__init__()

        self._positions: TransBuf = positions
        self._sizes: TransBuf = sizes
        self._face_colors: TransBuf = face_colors
        self._edge_colors: TransBuf = edge_colors
        self._edge_widths: TransBuf = edge_widths
        self._groups: Groups = groups

    # =============================================================================
    # get/set attributes
    # =============================================================================

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

    def get_groups(self) -> Groups:
        return self._groups

    def set_groups(self, groups: Groups) -> None:
        self._groups = groups
        self.check_attributes()

    def set_attributes(
        self,
        positions: TransBuf | None = None,
        sizes: TransBuf | None = None,
        face_colors: TransBuf | None = None,
        edge_colors: TransBuf | None = None,
        edge_widths: TransBuf | None = None,
        groups: Groups | None = None,
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
        if groups is not None:
            self._groups = groups
        self.check_attributes()

    # =============================================================================
    # Sanity check functions
    # =============================================================================

    def check_attributes(self) -> None:
        """Check that the attributes are valid and consistent."""
        self.sanity_check_attributes(self._positions, self._sizes, self._face_colors, self._edge_colors, self._edge_widths, self._groups)

    @staticmethod
    def sanity_check_attributes_buffer(positions: Buffer, sizes: Buffer, face_colors: Buffer, edge_colors: Buffer, edge_widths: Buffer, groups: Groups):
        """same as .sanity_check_attributes() but accept only Buffers.

        - It is meant to be used after converting TransBuf to Buffer.
        """
        # sanity check - each attribute must be a Buffer (not a transform chain)
        assert isinstance(positions, Buffer), "Positions must be a Buffer"
        assert isinstance(sizes, Buffer), "Sizes must be a Buffer"
        assert isinstance(face_colors, Buffer), "Face colors must be a Buffer"
        assert isinstance(edge_colors, Buffer), "Edge colors must be a Buffer"
        assert isinstance(edge_widths, Buffer), "Edge widths must be a Buffer"

        Points.sanity_check_attributes(positions, sizes, face_colors, edge_colors, edge_widths, groups)

    @staticmethod
    def sanity_check_attributes(
        positions: TransBuf,
        sizes: TransBuf,
        face_colors: TransBuf,
        edge_colors: TransBuf,
        edge_widths: TransBuf,
        groups: Groups,
    ) -> None:

        pass
