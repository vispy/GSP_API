"""Example rendering a mesh with MeshBasicMaterial (magenta faces + black wireframe)."""

# stdlib imports
import pathlib

# pip imports
import numpy as np

# local imports
from gsp.core import Canvas, Viewport, Camera
from gsp.materials.mesh_basic_material import MeshBasicMaterial
from gsp.types.visual_base import VisualBase
from gsp.visuals.mesh import Mesh
from gsp.types import BufferType
from gsp_extra.bufferx import Bufferx
from gsp_extra.misc.mesh_utils import MeshUtils
from gsp.constants import Constants
from common.example_helper import ExampleHelper
from gsp_extra.mpl3d import glm
from gsp.utils.transbuf_utils import TransBufUtils


def main():
    """Example rendering a mesh with MeshBasicMaterial (magenta faces + black wireframe)."""
    np.random.seed(0)

    canvas = Canvas(400, 400, 72.0, Constants.Color.white)
    viewport = Viewport(0, 0, canvas.get_width(), canvas.get_height(), Constants.Color.transparent)

    obj_path = pathlib.Path(__file__).parent / "models" / "suzanne.obj"
    mesh_geometry = MeshUtils.parse_obj_file_manual(str(obj_path))

    positions_buffer = TransBufUtils.to_buffer(mesh_geometry.get_positions())
    position_count = Bufferx.to_numpy(positions_buffer).reshape(-1, 3).shape[0]

    face_colors_buffer = Bufferx.from_numpy(np.array([[255, 0, 255, 255]] * position_count, dtype=np.uint8), BufferType.rgba8)
    edge_colors_buffer = Bufferx.from_numpy(np.array([Constants.Color.black], dtype=np.uint8), BufferType.rgba8)
    edge_widths_buffer = Bufferx.from_numpy(np.array([0.5], dtype=np.float32), BufferType.float32)
    mesh_material = MeshBasicMaterial(face_colors_buffer, edge_colors_buffer, edge_widths_buffer, True, Constants.FaceCulling.FrontSide)

    mesh = Mesh(mesh_geometry, mesh_material)

    model_matrix = Bufferx.from_numpy(np.array([np.eye(4, dtype=np.float32)]), BufferType.mat4)

    view_matrix_numpy = glm.lookat(eye=(0, 0, 4), center=(0, 0, 0), up=(0, 1, 0))
    projection_matrix_numpy = glm.perspective(fovy=45.0, aspect=canvas.get_width() / canvas.get_height(), znear=0.1, zfar=10.0)
    view_matrix = Bufferx.from_numpy(np.array([view_matrix_numpy], dtype=np.float32), BufferType.mat4)
    projection_matrix = Bufferx.from_numpy(np.array([projection_matrix_numpy], dtype=np.float32), BufferType.mat4)
    camera = Camera(view_matrix, projection_matrix)

    renderer_name = ExampleHelper.get_renderer_name()
    renderer_base = ExampleHelper.create_renderer(renderer_name, canvas)

    animator = ExampleHelper.create_animator(renderer_base)
    present = 0.0

    @animator.event_listener
    def animator_callback(delta_time: float) -> list[VisualBase]:
        nonlocal model_matrix, present
        present += delta_time
        angle_y = (present * 40) % 360
        matrix_mvp = glm.yrotate(angle_y)
        model_matrix = Bufferx.from_numpy(np.array([matrix_mvp]), BufferType.mat4)
        renderer_base.render([viewport], [mesh], [model_matrix], [camera])
        return []

    animator.start()


if __name__ == "__main__":
    main()
