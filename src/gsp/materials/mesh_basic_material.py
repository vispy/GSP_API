# pip imports
import numpy as np

# local imports
from ..constants import Constants
from .mesh_material import MeshMaterial
from ..types.transbuf import TransBuf


class MeshBasicMaterial(MeshMaterial):
    """A simple material class to hold texture mesh material properties."""

    __slots__ = "texture"

    def __init__(self, face_colors: TransBuf, edge_colors: TransBuf, edge_widths: TransBuf, face_sorting: bool, face_culling: Constants.FaceCulling):
        """Initialize a MeshBasicMaterial instance.

        Args:
            face_colors (TransBuf): Vertex colors of the mesh, shape (N, 4) RGBA format.
            edge_colors (TransBuf): array of point edge colors
            edge_widths (TransBuf): array of point edge widths
            face_sorting (bool, optional): Whether to sort faces by depth (painter's algorithm)
            face_culling (Constants.FaceCulling, optional): Whether to cull faces based on their orientation relative to the camera
        """
        super().__init__()

        self._face_colors: TransBuf = face_colors
        """Vertex colors of the mesh, shape (N, 4) RGBA format."""
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

    def get_colors(self) -> TransBuf:
        """Get the vertex colors.

        Returns:
            TransBuf: Vertex colors of the mesh, shape (N, 4) RGBA format.
        """
        return self._face_colors

    def set_colors(self, colors: TransBuf) -> None:
        """Set the vertex colors.

        Args:
            colors (TransBuf): Vertex colors of the mesh, shape (N, 4) RGBA format.
        """
        self._face_colors = colors
        self.check_attributes()

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
            bool: Whether to sort faces by depth (painter's algorithm).
        """
        return self._face_sorting

    def set_face_sorting(self, face_sorting: bool) -> None:
        """Set whether to sort faces by depth (painter's algorithm).

        Args:
            face_sorting (bool): Whether to sort faces by depth (painter's algorithm).
        """
        self._face_sorting = face_sorting
        self.check_attributes()

    def get_face_culling(self) -> Constants.FaceCulling:
        """Get whether to cull faces based on their orientation relative to the camera.

        Returns:
            Constants.FaceCulling: Whether to cull faces based on their orientation relative to the camera.
        """
        return self._face_culling

    def set_face_culling(self, face_culling: Constants.FaceCulling) -> None:
        """Set whether to cull faces based on their orientation relative to the camera.

        Args:
            face_culling (Constants.FaceCulling): Whether to cull faces based on their orientation relative to the camera.
        """
        self._face_culling = face_culling
        self.check_attributes()

    # =============================================================================
    # Sanity check functions
    # =============================================================================

    def check_attributes(self) -> None:
        """Check that the attributes are valid and consistent."""
        self.sanity_check_attributes(self._face_colors)

    @staticmethod
    def sanity_check_attributes_buffer(
        colors: TransBuf,
    ) -> None:
        """Same as .sanity_check_attributes() but accept only Buffers.

        Args:
            colors (TransBuf): The vertex colors.
        """
        MeshBasicMaterial.sanity_check_attributes(colors)

    @staticmethod
    def sanity_check_attributes(
        colors: TransBuf,
    ) -> None:
        """Check that the geometry attributes are valid and consistent.

        Args:
            colors (TransBuf): The vertex colors of the mesh, BufType.rgba8.
        """
        pass
