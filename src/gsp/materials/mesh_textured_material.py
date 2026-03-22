# pip imports
import numpy as np


# local imports
from ..constants import Constants
from ..core import Texture
from .mesh_material import MeshMaterial


class MeshTexturedMaterial(MeshMaterial):
    """A simple material class to hold texture mesh material properties."""

    __slots__ = "texture"

    def __init__(
        self,
        texture: Texture,
        color: np.ndarray | None = None,
        shininess: float | None = None,
        face_sorting: bool | None = None,
        face_culling: Constants.FaceCulling | None = None,
    ):
        """Initialize a MeshTexturedMaterial instance."""
        super().__init__()

        self.color: np.ndarray = color if color is not None else np.array([Constants.Color.white]).astype(np.float32)
        """Base color of the material, as an (R, G, B, A) array with values in [0, 1]. shape (4,)"""
        self.shininess: float = shininess if shininess is not None else 30.0
        """Shininess factor for specular highlights."""
        self.texture: Texture = texture
        """Texture for the TextureMeshMaterial."""
        self.face_sorting: bool = face_sorting if face_sorting is not None else True
        """Whether to sort faces by depth (painter's algorithm)."""
        self.face_culling: Constants.FaceCulling = face_culling if face_culling is not None else Constants.FaceCulling.FrontSide
        """Whether to cull faces based on their orientation relative to the camera."""
