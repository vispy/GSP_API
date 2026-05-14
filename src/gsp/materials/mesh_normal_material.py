"""MeshNormalMaterial: colors each face by its view-space normal direction."""

# local imports
from ..constants import Constants
from .mesh_material import MeshMaterial
from ..types.transbuf import TransBuf
from ..types.buffer_type import BufferType
from ..types.buffer import Buffer
from ..utils.transbuf_utils import TransBufUtils


class MeshNormalMaterial(MeshMaterial):
    """A material that colors each face by its view-space normal direction."""

    def __init__(self, edge_colors: TransBuf, edge_widths: TransBuf, face_sorting: bool, face_culling: Constants.FaceCulling):
        """Initialize a MeshNormalMaterial instance.

        Face colors are computed at render time from the view-space normal of each face;
        there is no face_colors attribute.

        Args:
            edge_colors (TransBuf): array of edge colors, rgba8.
            edge_widths (TransBuf): array of edge widths.
            face_sorting (bool): Whether to sort faces by depth (painter's algorithm).
            face_culling (Constants.FaceCulling): Whether to cull faces based on orientation relative to the camera.
        """
        super().__init__()

        self._edge_colors: TransBuf = edge_colors
        """Edge colors of the mesh, shape (N, 4)."""
        self._edge_widths: TransBuf = edge_widths
        """Edge widths of the mesh, shape (N,)."""
        self._face_sorting: bool = face_sorting if face_sorting is not None else True
        """Whether to sort faces by depth (painter's algorithm)."""
        self._face_culling: Constants.FaceCulling = face_culling if face_culling is not None else Constants.FaceCulling.FrontSide
        """Whether to cull faces based on their orientation relative to the camera."""

    # =============================================================================
    # get/set attributes
    # =============================================================================

    def get_edge_colors(self) -> TransBuf:
        """Get the edge colors.

        Returns:
            TransBuf: Edge colors of the mesh, shape (N, 4).
        """
        return self._edge_colors

    def set_edge_colors(self, edge_colors: TransBuf) -> None:
        """Set the edge colors.

        Args:
            edge_colors (TransBuf): Edge colors of the mesh, shape (N, 4).
        """
        self._edge_colors = edge_colors
        self.check_attributes()

    def get_edge_widths(self) -> TransBuf:
        """Get the edge widths.

        Returns:
            TransBuf: Edge widths of the mesh, shape (N,).
        """
        return self._edge_widths

    def set_edge_widths(self, edge_widths: TransBuf) -> None:
        """Set the edge widths.

        Args:
            edge_widths (TransBuf): Edge widths of the mesh, shape (N,).
        """
        self._edge_widths = edge_widths
        self.check_attributes()

    def get_face_sorting(self) -> bool:
        """Get whether to sort faces by depth (painter's algorithm).

        Returns:
            bool: Whether to sort faces by depth.
        """
        return self._face_sorting

    def set_face_sorting(self, face_sorting: bool) -> None:
        """Set whether to sort faces by depth (painter's algorithm).

        Args:
            face_sorting (bool): Whether to sort faces by depth.
        """
        self._face_sorting = face_sorting
        self.check_attributes()

    def get_face_culling(self) -> Constants.FaceCulling:
        """Get whether to cull faces based on their orientation relative to the camera.

        Returns:
            Constants.FaceCulling: Face culling mode.
        """
        return self._face_culling

    def set_face_culling(self, face_culling: Constants.FaceCulling) -> None:
        """Set whether to cull faces based on their orientation relative to the camera.

        Args:
            face_culling (Constants.FaceCulling): Face culling mode.
        """
        self._face_culling = face_culling
        self.check_attributes()

    # =============================================================================
    # Sanity check functions
    # =============================================================================

    def check_attributes(self) -> None:
        """Check that the attributes are valid and consistent."""
        self.sanity_check_attributes()

    def check_attributes_buffer(self) -> None:
        """Check that the attribute buffers are valid and consistent."""
        edge_colors_buffer = TransBufUtils.to_buffer(self._edge_colors)
        self.sanity_check_attributes_buffer(edge_colors_buffer)

    @staticmethod
    def sanity_check_attributes_buffer(
        edge_colors: Buffer,
    ) -> None:
        """Check that the geometry attribute buffers are valid and consistent.

        Args:
            edge_colors (TransBuf): The edge colors.
        """
        assert edge_colors.get_type() == BufferType.rgba8, f"edge_colors buffer must be rgba8, got {edge_colors.get_type()}"

    @staticmethod
    def sanity_check_attributes() -> None:
        """Check pre-buffer attributes (currently nothing to check)."""
        pass
