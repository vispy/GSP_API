# stdlib imports
from typing import Sequence

# pip imports
import numpy as np

# local imports
from .bufferx import Bufferx
from gsp.core.visual_base import VisualBase
from gsp.core.camera import Camera
from . import glm
from gsp.core import Canvas, Viewport, VisualBase
from gsp_matplotlib.renderer import MatplotlibRenderer
from gsp.types import Buffer, BufferType
from gsp.utils.uuid_utils import UuidUtils


class Object3D:

    def __init__(self, name: str | None = None):
        self.uuid = UuidUtils.generate_uuid()
        """uuid of the visual being wrapped."""

        self.name: str = name if name is not None else f"a {self.__class__.__name__} - {self.uuid}"
        """name of this Object3D."""

        self.matrix_world: np.ndarray = np.eye(4, dtype=np.float32)
        """matrix world of this Object3D"""
        self.matrix_local: np.ndarray = np.eye(4, dtype=np.float32)
        """matrix local of this Object3D"""

        self.dont_update_matrix_world: bool = False
        """if True, the world matrix won't be updated."""
        self.dont_update_matrix_local: bool = False
        """if True, the local matrix won't be updated."""

        self.rotation_order: str = "XYZ"
        """rotation order for euler angles."""
        self.position: np.ndarray = np.zeros(3, dtype=np.float32)
        """position of this Object3D."""
        self.euler: np.ndarray = np.zeros(3, dtype=np.float32)
        """euler angles in radians of this Object3D."""
        self.scale: np.ndarray = np.ones(3, dtype=np.float32)
        """scale of this Object3D."""

        self.children: list[Object3D] = []
        """list of children Object3D."""

        self.visuals: list[VisualBase] = []
        """list of visuals attached to this Object3D."""
        self.cameras: list[Camera] = []
        """list of cameras attached to this Object3D."""

    def __repr__(self) -> str:
        return f"Object3D(name={self.name})"

    # =============================================================================
    # .add/.remove
    # =============================================================================

    def add(self, child: "Object3D"):
        """Add a child Object3D to this Object3D.

        Args:
            child (Object3D): child to add.
        """
        self.children.append(child)

    def remove(self, child: "Object3D"):
        """Remove a child Object3D from this Object3D.

        Args:
            child (Object3D): child to remove.
        """
        self.children.remove(child)

    # =============================================================================
    # .attach_visual/.detach_visual
    # =============================================================================

    def attach_visual(self, visual: VisualBase):
        """Add a visual to this Object3D.

        Args:
            visual (VisualBase): visual to add.
        """
        self.visuals.append(visual)

    def detach_visual(self, visual: VisualBase):
        """Remove a visual from this Object3D.

        Args:
            visual (VisualBase): visual to remove.
        """
        self.visuals.remove(visual)

    # =============================================================================
    # .attach_camera/.detach_camera
    # =============================================================================

    def attach_camera(self, camera: Camera):
        """Add a camera to this Object3D.

        Args:
            camera (Camera): camera to add.
        """
        self.cameras.append(camera)

    def detach_camera(self, camera: Camera):
        """Remove a camera from this Object3D.

        Args:
            camera (Camera): camera to remove.
        """
        self.cameras.remove(camera)

    # =============================================================================
    # .traverse
    # =============================================================================

    def traverse(self):
        """Generator to traverse the Object3D hierarchy."""
        yield self
        for child in self.children:
            yield from child.traverse()

    # =============================================================================
    # .update_matrix_*
    # =============================================================================

    def update_matrix_local(self, force_update: bool = False):
        """Upload the local matrix from position, euler and scale."""

        # honor dont_update_matrix_local flag
        if self.dont_update_matrix_local and not force_update:
            return

        # compute the scale matrix
        scale_matrix = glm.scale(self.scale)

        # compute the rotation matrix in the specified order
        rotation_matrix = np.eye(4, dtype=np.float32)
        for axis in self.rotation_order:
            if axis == "X":
                rotation_matrix = rotation_matrix @ glm.xrotate(self.euler[0] / np.pi * 180.0)
            elif axis == "Y":
                rotation_matrix = rotation_matrix @ glm.yrotate(self.euler[1] / np.pi * 180.0)
            elif axis == "Z":
                rotation_matrix = rotation_matrix @ glm.zrotate(self.euler[2] / np.pi * 180.0)

        # compute the translation matrix
        translation_matrix = glm.translate(self.position)

        # set the local matrix
        self.matrix_local = translation_matrix @ rotation_matrix @ scale_matrix

    def update_matrix_world(self, parent_matrix_world: np.ndarray | None = None, force_update: bool = False):
        """Compute the world matrix from the local matrix and the parent's world matrix.

        Args:
            parent_matrix_world (np.ndarray | None): parent's world matrix. Defaults to None.
        """
        # update local matrix
        self.update_matrix_local(force_update=force_update)

        # update world matrix - honor dont_update_matrix_world flag
        if parent_matrix_world is None:
            self.matrix_world = self.matrix_local
        elif not self.dont_update_matrix_world or force_update:
            self.matrix_world = parent_matrix_world @ self.matrix_local

        # update children
        for child in self.children:
            child.update_matrix_world(self.matrix_world)

    # =============================================================================
    #
    # =============================================================================
    @staticmethod
    def render(matplotlibRenderer: MatplotlibRenderer, viewport: Viewport, scene: "Object3D", camera: Camera) -> Sequence[VisualBase]:
        # update all world matrices
        scene.update_matrix_world()

        # update camera view matrices
        for object3d in scene.traverse():
            for _camera in object3d.cameras:
                view_matrix_numpy = np.linalg.inv(object3d.matrix_world)
                view_matrix_buffer = Bufferx.from_numpy(np.array([view_matrix_numpy]), BufferType.mat4)
                _camera.set_view_matrix(view_matrix_buffer)

        # gather all visuals, model matrices and cameras
        visuals = [visual for object3d in scene.traverse() for visual in object3d.visuals]
        model_matrices_numpy = [object3d.matrix_world for object3d in scene.traverse() for _ in object3d.visuals]
        model_matrices_buffer = [Bufferx.from_numpy(np.array([model_matrix_numpy]), BufferType.mat4) for model_matrix_numpy in model_matrices_numpy]
        viewports = [viewport for _ in range(len(visuals))]
        cameras = [camera for _ in range(len(visuals))]

        # render all
        matplotlibRenderer.render(viewports, visuals, model_matrices_buffer, cameras)

        # return the modified visuals
        return visuals
