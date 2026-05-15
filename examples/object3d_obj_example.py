"""Example showing how to use Object3D to render the suzanne.obj vertex cloud as rotating Points."""

# stdlib imports
import pathlib

# pip imports
import numpy as np


# local imports
from common.example_helper import ExampleHelper
from gsp.core import Canvas, Viewport
from gsp.visuals import Points
from gsp.types import Buffer, BufferType
from gsp.types.visual_base import VisualBase
from gsp.core import Camera
from gsp_extra.bufferx import Bufferx
from gsp_extra.object3d import Object3D
from gsp_extra.misc.mesh_utils import MeshUtils
from gsp.constants import Constants
import gsp_extra.mpl3d.glm as glm
from gsp.utils.transbuf_utils import TransBufUtils
from gsp.utils.unit_utils import UnitUtils


def main():
    # Create a canvas
    canvas = Canvas(400, 400, 72.0, Constants.Color.white)

    # Create a viewport and add it to the canvas
    viewport = Viewport(0, 0, canvas.get_width(), canvas.get_height(), Constants.Color.transparent)

    # =============================================================================
    # Load suzanne.obj and use its vertices as the point cloud
    # =============================================================================

    obj_path = pathlib.Path(__file__).parent / "models" / "suzanne.obj"
    mesh_geometry = MeshUtils.parse_obj_file_manual(str(obj_path))

    positions_numpy = Bufferx.to_numpy(TransBufUtils.to_buffer(mesh_geometry.get_positions())).reshape(-1, 3).astype(np.float32)
    point_count = positions_numpy.shape[0]

    positions_buffer = Bufferx.from_numpy(positions_numpy, BufferType.vec3)

    # Sizes - one per point (in points)
    sizes_buffer = Bufferx.from_numpy(np.full(point_count, 5.0, dtype=np.float32), BufferType.float32)

    # all face colors red
    face_colors_buffer = Buffer(point_count, BufferType.rgba8)
    face_colors_buffer.set_data(bytearray([255, 0, 0, 255]) * point_count, 0, point_count)

    # Edge colors - black
    edge_colors_buffer = Buffer(point_count, BufferType.rgba8)
    edge_colors_buffer.set_data(Constants.Color.black * point_count, 0, point_count)

    # Edge widths - 1 pixel
    edge_widths_numpy = np.full(point_count, UnitUtils.pixel_to_point(1, canvas.get_dpi()), dtype=np.float32)
    edge_widths_buffer = Bufferx.from_numpy(edge_widths_numpy, BufferType.float32)

    points = Points(positions_buffer, sizes_buffer, face_colors_buffer, edge_colors_buffer, edge_widths_buffer)

    # =============================================================================
    # Build the scene
    # =============================================================================

    object3d_scene = Object3D("Main Scene")

    object3d_points = Object3D("Points Object3D")
    object3d_points.attach_visual(points)
    object3d_scene.add(object3d_points)

    # =============================================================================
    # Camera (fixes issue #22)
    # =============================================================================

    # Real lookat + perspective camera; identity matrices view from the wrong
    # side of OpenGL's NDC convention. Fixes
    # https://github.com/vispy/GSP_API/issues/22
    view_matrix_numpy = glm.lookat(eye=(0, 0, 4), center=(0, 0, 0), up=(0, 1, 0))
    projection_matrix_numpy = glm.perspective(
            fovy=45.0,
            aspect=canvas.get_width() / canvas.get_height(),
            znear=0.1,
            zfar=10.0,
    )
    view_matrix = Bufferx.from_numpy(np.array([view_matrix_numpy], dtype=np.float32), BufferType.mat4)
    projection_matrix = Bufferx.from_numpy(np.array([projection_matrix_numpy], dtype=np.float32), BufferType.mat4)
    camera = Camera(view_matrix, projection_matrix)

    # =============================================================================
    #
    # =============================================================================

    object3d_points.euler[0] = np.pi / 4
    object3d_points.euler[1] = np.pi / 4
    object3d_points.euler[2] = np.pi / 4

    # =============================================================================
    # Pre-compute render args
    # =============================================================================

    viewports, visuals, model_matrices, cameras = Object3D.pre_render(viewport, object3d_scene, camera)

    # =============================================================================
    # Create the renderer
    # =============================================================================

    renderer_name = ExampleHelper.get_renderer_name()
    renderer_base = ExampleHelper.create_renderer(renderer_name, canvas)
    animator = ExampleHelper.create_animator(renderer_base)

    elapsed = 0.0

    @animator.event_listener
    def animator_callback(delta_time: float) -> list[VisualBase]:
        nonlocal model_matrices, elapsed
        elapsed += delta_time

        # Linear continuous rotation: each axis spins at a different constant rate (rad/s).
        # No modulo - glm.{x,y,z}rotate handles unbounded angles via sin/cos.
        object3d_points.euler[0] = -elapsed * 1.0
        object3d_points.euler[1] = -elapsed * 2.0
        object3d_points.euler[2] = -elapsed * 3.0

        # Sinusoidal "breathing" scale in [0.3, 1.3]. By nature a sine is smooth
        # but not constant-rate (slows at the peaks). Replace with a triangle
        # wave if you want a constant zoom rate.
        object3d_points.scale[:] = 0.8 + 0.5 * np.sin(elapsed)

        # Re-compute render args
        _, _, _model_matrices, _cameras = Object3D.pre_render(viewport, object3d_scene, camera)

        # Update model_matrices and cameras in the render args for the animator
        for visual_index in range(model_matrices.__len__()):
            model_matrices[visual_index] = _model_matrices[visual_index]
            cameras[visual_index] = _cameras[visual_index]

        # return the modified visuals
        changed_visuals = [visual for object3d in object3d_scene.traverse() for visual in object3d.visuals]
        return changed_visuals

    # start the animation loop
    animator.start(viewports, visuals, model_matrices, cameras)


if __name__ == "__main__":
    main()
