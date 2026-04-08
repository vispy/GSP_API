"""Example showing how to use the Pixels visual to render a set of points."""

# stdlib imports
import pathlib
import os
import time

# pip imports
import numpy as np

# local imports
from gsp.core import Canvas, Viewport
from gsp.materials.mesh_depth_material import MeshDepthMaterial
from gsp.materials.mesh_normal_material import MeshNormalMaterial
from gsp.types.visual_base import VisualBase
from gsp.visuals.mesh import Mesh
from gsp.types import Buffer, BufferType
from gsp.geometry import MeshGeometry
from gsp.materials import MeshBasicMaterial
from gsp.core import Camera
from gsp_extra.bufferx import Bufferx
from gsp_extra.misc.mesh_utils import MeshUtils
from gsp.utils.group_utils import GroupUtils
from gsp.constants import Constants
from common.example_helper import ExampleHelper
from gsp_extra.mpl3d import glm


def main():
    """Main function for the pixels example."""
    # fix random seed for reproducibility
    np.random.seed(0)

    # Create a canvas
    canvas = Canvas(400, 400, 72.0, Constants.Color.white)

    # Create a viewport and add it to the canvas
    viewport = Viewport(0, 0, canvas.get_width(), canvas.get_height(), Constants.Color.transparent)

    # =============================================================================
    # Add random points
    # - various ways to create Buffers
    # =============================================================================

    # Load a obj geometry
    # obj_path = pathlib.Path(__file__).parent / "models" / "triangle.obj"
    # obj_path = pathlib.Path(__file__).parent / "models" / "cube.obj"
    obj_path = pathlib.Path(__file__).parent / "models" / "head.obj"
    mesh_geometry = MeshUtils.parse_obj_file_manual(str(obj_path))

    # mesh_material = MeshBasicMaterial()
    # mesh_material = MeshDepthMaterial()
    mesh_material = MeshNormalMaterial()
    # mesh_material.colors = np.array([255, 0, 255, 255], dtype=np.float32)  # red, green, blue
    # mesh_material.face_sorting = True
    mesh_material.face_culling = Constants.FaceCulling.FrontSide

    # Create a mesh
    mesh = Mesh(mesh_geometry, mesh_material)

    # =============================================================================
    # Render the canvas
    # =============================================================================

    # Model matrix
    model_matrix = Bufferx.mat4_identity()

    model_matrix_numpy = glm.xrotate() @ glm.yrotate(0.0) @ glm.zrotate(0)
    # axes_transform_numpy = glm.translate(np.array([0.0, 0.0, 0.0])) @ glm.scale(np.array([0.5, 2, 0.5]))
    # model_matrix_numpy = axes_transform_numpy @ model_matrix_numpy
    model_matrix = Bufferx.from_numpy(np.array([model_matrix_numpy]), BufferType.mat4)

    # Create a camera
    camera = Camera(Bufferx.mat4_identity(), Bufferx.mat4_identity())

    # =============================================================================
    # Render
    # =============================================================================

    # Create renderer and render
    renderer_name = ExampleHelper.get_renderer_name()
    renderer_base = ExampleHelper.create_renderer(renderer_name, canvas)
    animator = ExampleHelper.create_animator(renderer_base)

    present = 0

    @animator.event_listener
    def animator_callback(delta_time: float) -> list[VisualBase]:
        nonlocal model_matrix, present

        present += delta_time

        angle_x = 0
        angle_y = 0
        angle_z = 0

        # angle_x = (present * 40) % 360
        angle_y = (present * 40) % 360
        # angle_z = (present * 40) % 360

        position_x = 0.0
        position_y = 0.0
        position_z = 0.0

        scale_x = 0.5
        scale_y = 0.5
        scale_z = 0.5

        matrix_rotation = glm.xrotate(angle_x) @ glm.yrotate(angle_y) @ glm.zrotate(angle_z)
        matrix_translation = glm.translate(np.array([position_x, position_y, position_z]))
        matrix_scale = glm.scale(np.array([scale_x, scale_y, scale_z]))

        matrix_mvp = matrix_translation @ matrix_scale @ matrix_rotation

        model_matrix = Bufferx.from_numpy(np.array([matrix_mvp]), BufferType.mat4)

        renderer_base.render([viewport], [mesh], [model_matrix], [camera])
        changed_visuals: list[VisualBase] = []
        return changed_visuals

    animator.start()


if __name__ == "__main__":
    main()
