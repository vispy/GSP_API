# pip imports
import numpy as np

# local imports
from .geometry import Geometry
from ..types.transbuf import TransBuf


class MeshGeometry(Geometry):
    """A class representing a 3D geometry with vertices, faces, texture coordinates, and normals."""

    __slots__ = ("_indices", "_uvs", "_normals")

    def __init__(
        self,
        vertices: TransBuf,
        indices: TransBuf,
        uvs: TransBuf,
        normals: TransBuf,
    ):
        """A class representing a 3D geometry with vertices, faces, texture coordinates, and normals. Only triangular faces are supported.

        Arguments:
            vertices (TransBuf): array of vertex coordinates, shape (N, 3)
            indices (TransBuf): array of face indices, shape (M, 3)
            uvs (TransBuf): array of texture coordinates, shape (N, 2)
            normals (TransBuf): array of normal coordinates, shape (N, 3)
        """
        super().__init__(vertices)

        # assign attributes
        self._indices: TransBuf = indices
        self._uvs: TransBuf = uvs
        self._normals: TransBuf = normals

    # =============================================================================
    # get/set attributes
    # =============================================================================

    def get_indices(self) -> TransBuf:
        """Get the face indices.

        Returns:
            TransBuf: array of face indices, shape (M, 3)
        """
        return self._indices

    def set_indices(self, indices: TransBuf) -> None:
        """Set the face indices.

        Args:
            indices (TransBuf): array of face indices, shape (M, 3)
        """
        self._indices = indices
        self.check_attributes()

    def get_uvs(self) -> TransBuf:
        """Get the texture coordinates.

        Returns:
            TransBuf: array of texture coordinates, shape (N, 2)
        """
        return self._uvs

    def set_uvs(self, uvs: TransBuf) -> None:
        """Set the texture coordinates.

        Args:
            uvs (TransBuf): array of texture coordinates, shape (N, 2)
        """
        self._uvs = uvs
        self.check_attributes()

    def get_normals(self) -> TransBuf:
        """Get the normal coordinates.

        Returns:
            TransBuf: array of normal coordinates, shape (N, 3)
        """
        return self._normals

    def set_normals(self, normals: TransBuf) -> None:
        """Set the normal coordinates.

        Args:
            normals (TransBuf): array of normal coordinates, shape (N, 3)
        """
        self._normals = normals
        self.check_attributes()

    # =============================================================================
    # Sanity check functions
    # =============================================================================

    def check_attributes(self) -> None:
        """Check that the attributes are valid and consistent."""
        self.sanity_check_attributes(self._vertices, self._indices, self._uvs, self._normals)

    @staticmethod
    def sanity_check_attributes_buffer(
        vertices: TransBuf,
        indices: TransBuf,
        uvs: TransBuf,
        normals: TransBuf,
    ) -> None:
        """Same as .sanity_check_attributes() but accept only Buffers.

        Args:
            vertices (TransBuf): The vertex coordinates.
            indices (TransBuf): The face indices.
            uvs (TransBuf): The texture coordinates.
            normals (TransBuf): The normal coordinates.
        """
        MeshGeometry.sanity_check_attributes(vertices, indices, uvs, normals)

    @staticmethod
    def sanity_check_attributes(
        vertices: TransBuf,
        indices: TransBuf,
        uvs: TransBuf,
        normals: TransBuf,
    ) -> None:
        """Check that the geometry attributes are valid and consistent.

        Args:
            vertices (TransBuf): The vertex coordinates.
            indices (TransBuf): The face indices.
            uvs (TransBuf): The texture coordinates.
            normals (TransBuf): The normal coordinates.
        """
        pass
