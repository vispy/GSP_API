# pip imports
import numpy as np

from ..constants import Constants

# local imports
from .material import Material
from ..core import Texture
from .mesh_material import MeshMaterial


class MeshNormalMaterial(MeshMaterial):
    """A simple material class to hold texture mesh material properties."""

    __slots__ = "texture"

    def __init__(
        self,
        edge_colors: np.ndarray | None = None,
        edge_widths: np.ndarray | None = None,
        face_sorting: bool | None = None,
        face_culling: Constants.FaceCulling | None = None,
    ):
        super().__init__()

        self.edge_colors: np.ndarray = edge_colors if edge_colors is not None else np.array([Constants.Color.black]).astype(np.float32)
        """array of point edge colors, shape (N, 3) or (N, 4)"""
        self.edge_widths: np.ndarray = edge_widths if edge_widths is not None else np.array([0.2]).astype(np.float32)
        """array of point edge widths, shape (N,)"""
        self.face_sorting: bool = face_sorting if face_sorting is not None else True
        """Whether to sort faces by depth (painter's algorithm)."""
        self.face_culling: Constants.FaceCulling = face_culling if face_culling is not None else Constants.FaceCulling.FrontSide
        """Whether to cull faces based on their orientation relative to the camera."""
