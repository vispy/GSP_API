"""Example showing how to use the Pixels visual to render a set of points."""

# stdlib imports
import pathlib
import os
import time

# pip imports
import numpy as np

# local imports
from typing import Sequence

from gsp.core import Canvas, Viewport
from gsp.lights.ambient_light import AmbientLight
from gsp.lights.directional_light import DirectionalLight
from gsp.lights.light import Light
from gsp.materials.mesh_basic_material import MeshBasicMaterial
from gsp.materials.mesh_normal_material import MeshNormalMaterial
from gsp.materials.mesh_depth_material import MeshDepthMaterial
from gsp.materials.mesh_phong_material import MeshPhongMaterial
from gsp.types.visual_base import VisualBase
from gsp.visuals.mesh import Mesh
from gsp.types import Buffer, BufferType  # noqa: F401 -- Buffer used as a return annotation
from gsp.geometry import MeshGeometry
from gsp.core import Camera
from gsp_extra.bufferx import Bufferx
from gsp_extra.misc.mesh_utils import MeshUtils
from gsp.utils.group_utils import GroupUtils
from gsp.constants import Constants
from common.example_helper import ExampleHelper
from gsp_extra.mpl3d import glm
from gsp.utils.transbuf_utils import TransBufUtils


def create_basic_material(position_count: int) -> MeshBasicMaterial:
    """Create a MeshBasicMaterial with magenta faces and a thin black wireframe."""
    face_colors_numpy = np.array([[255, 0, 255, 255]] * position_count, dtype=np.uint8)
    face_colors_buffer = Bufferx.from_numpy(face_colors_numpy, BufferType.rgba8)
    edge_colors_buffer = Bufferx.from_numpy(np.array([Constants.Color.black], dtype=np.uint8), BufferType.rgba8)
    edge_widths_buffer = Bufferx.from_numpy(np.array([0.5], dtype=np.float32), BufferType.float32)
    return MeshBasicMaterial(face_colors_buffer, edge_colors_buffer, edge_widths_buffer, True, Constants.FaceCulling.FrontSide)


def create_normal_material() -> MeshNormalMaterial:
    """Create a MeshNormalMaterial; face colors are derived from view-space normals at render time."""
    edge_colors_buffer = Bufferx.from_numpy(np.array([Constants.Color.black], dtype=np.uint8), BufferType.rgba8)
    edge_widths_buffer = Bufferx.from_numpy(np.array([0.5], dtype=np.float32), BufferType.float32)
    return MeshNormalMaterial(edge_colors_buffer, edge_widths_buffer, True, Constants.FaceCulling.FrontSide)


def create_depth_material() -> MeshDepthMaterial:
    """Create a MeshDepthMaterial; face colors are derived from view-space depth at render time."""
    edge_colors_buffer = Bufferx.from_numpy(np.array([Constants.Color.black], dtype=np.uint8), BufferType.rgba8)
    edge_widths_buffer = Bufferx.from_numpy(np.array([0.5], dtype=np.float32), BufferType.float32)
    return MeshDepthMaterial(edge_colors_buffer, edge_widths_buffer, True, Constants.FaceCulling.FrontSide)


# Intended world-space positions for the Phong directional light.
# Used both for the initial lights setup (when model_matrix is identity, model space == world space)
# and by update_phong_lights_world_fixed() to keep the light anchored as the mesh rotates.
PHONG_DIRECTIONAL_LIGHT_WORLD_POSITION = np.array([5.0, 5.0, 5.0], dtype=np.float32)
PHONG_DIRECTIONAL_TARGET_WORLD_POSITION = np.array([0.0, 0.0, 0.0], dtype=np.float32)


def create_phong_lights() -> Sequence[Light]:
    """Build a small default light scene: one ambient + one directional. Positions are in model space."""
    light_position = Bufferx.from_numpy(PHONG_DIRECTIONAL_LIGHT_WORLD_POSITION.reshape(1, 3), BufferType.vec3)
    target_position = Bufferx.from_numpy(PHONG_DIRECTIONAL_TARGET_WORLD_POSITION.reshape(1, 3), BufferType.vec3)
    return [
        AmbientLight(color=Constants.Color.gray, intensity=0.3),
        DirectionalLight(
            light_position=light_position,
            target_position=target_position,
            color=Constants.Color.white,
            intensity=0.8,
        ),
    ]


def update_phong_lights_world_fixed(lights: Sequence[Light], model_matrix_numpy: np.ndarray) -> None:
    """Anchor each light at its world-space position even as the mesh's model_matrix changes.

    Since light positions are stored in model space and transformed by model_matrix at render time,
    setting model_space_pos = inverse(model_matrix) @ desired_world_pos cancels out the model
    transform and the light appears fixed in world space.
    """
    inverse_model = np.linalg.inv(model_matrix_numpy)

    def to_model_space_buffer(world_position: np.ndarray) -> Buffer:
        world_homogeneous = np.append(world_position, 1.0)
        model_xyz = (inverse_model @ world_homogeneous)[:3].astype(np.float32)
        return Bufferx.from_numpy(model_xyz.reshape(1, 3), BufferType.vec3)

    for light in lights:
        if isinstance(light, DirectionalLight):
            light.set_light_position(to_model_space_buffer(PHONG_DIRECTIONAL_LIGHT_WORLD_POSITION))
            light.set_target_position(to_model_space_buffer(PHONG_DIRECTIONAL_TARGET_WORLD_POSITION))


def create_phong_material(position_count: int) -> MeshPhongMaterial:
    """Create a MeshPhongMaterial with a default light setup; flat per-face Phong shading."""
    diffuse_color = Bufferx.from_numpy(np.array([[255, 0, 255, 255]] * position_count, dtype=np.uint8), BufferType.rgba8)
    specular_color = Bufferx.from_numpy(np.array([[255, 255, 255, 255]], dtype=np.uint8), BufferType.rgba8)
    edge_colors_buffer = Bufferx.from_numpy(np.array([Constants.Color.black], dtype=np.uint8), BufferType.rgba8)
    edge_widths_buffer = Bufferx.from_numpy(np.array([0.5], dtype=np.float32), BufferType.float32)
    lights = create_phong_lights()
    return MeshPhongMaterial(
        diffuse_color,
        specular_color,
        32.0,
        lights,
        edge_colors_buffer,
        edge_widths_buffer,
        True,
        Constants.FaceCulling.FrontSide,
    )


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
    # obj_path = pathlib.Path(__file__).parent / "models" / "cube.obj"
    obj_path = pathlib.Path(__file__).parent / "models" / "suzanne.obj"
    # obj_path = pathlib.Path(__file__).parent / "models" / "head.obj"
    mesh_geometry = MeshUtils.parse_obj_file_manual(str(obj_path))

    positions_buffer = TransBufUtils.to_buffer(mesh_geometry.get_positions())
    positions_numpy = Bufferx.to_numpy(positions_buffer).reshape(-1, 3)
    position_count = positions_numpy.shape[0]

    # Pick which material to render with: "basic" | "normal" | "depth" | "phong"
    material_type = "phong"
    if material_type == "basic":
        mesh_material = create_basic_material(position_count)
    elif material_type == "normal":
        mesh_material = create_normal_material()
    elif material_type == "depth":
        mesh_material = create_depth_material()
    elif material_type == "phong":
        mesh_material = create_phong_material(position_count)
    else:
        raise ValueError(f"Unknown material_type {material_type!r}")

    if False:
        position_x = 0.0
        position_y = 0.0
        position_z = -0.5
        angle_x = 0.0
        angle_y = 45.0
        angle_z = 0.0
        scale_x = 1.0
        scale_y = 1.0
        scale_z = 1.0

        model_matrix_numpy = glm.xrotate(angle_x) @ glm.yrotate(angle_y) @ glm.zrotate(angle_z)
        axes_transform_numpy = glm.translate(np.array([position_x, position_y, position_z])) @ glm.scale(np.array([scale_x, scale_y, scale_z]))
        model_matrix_numpy = axes_transform_numpy @ model_matrix_numpy
        model_matrix = Bufferx.from_numpy(np.array([model_matrix_numpy]), BufferType.mat4)

        positions_numpy = Bufferx.to_numpy(TransBufUtils.to_buffer(mesh_geometry.get_positions()))
        positions_numpy = positions_numpy @ model_matrix_numpy[:3, :3].T + model_matrix_numpy[:3, 3]

        positions_buffer = Bufferx.from_numpy(positions_numpy, BufferType.vec3)
        mesh_geometry.set_positions(positions_buffer)

    # positions_numpy = Bufferx.to_numpy(TransBufUtils.to_buffer(mesh_geometry.get_positions()))
    # print("positions_numpy", positions_numpy.tolist())

    # Create a mesh
    mesh = Mesh(mesh_geometry, mesh_material)

    # =============================================================================
    # Render the canvas
    # =============================================================================

    # Model matrix
    model_matrix = Bufferx.mat4_identity()

    position_x = 0.0
    position_y = 0.0
    position_z = 0.0
    angle_x = 0.0
    angle_y = 0.0
    angle_z = 0.0
    scale_x = 1.0
    scale_y = 1.0
    scale_z = 1.0

    model_matrix_numpy = glm.xrotate(angle_x) @ glm.yrotate(angle_y) @ glm.zrotate(angle_z)
    axes_transform_numpy = glm.translate(np.array([position_x, position_y, position_z])) @ glm.scale(np.array([scale_x, scale_y, scale_z]))
    model_matrix_numpy = axes_transform_numpy @ model_matrix_numpy
    model_matrix = Bufferx.from_numpy(np.array([model_matrix_numpy]), BufferType.mat4)

    # Real lookat + perspective camera; identity matrices view from the wrong
    # side of OpenGL's NDC convention. See
    # https://github.com/vispy/GSP_API/issues/21#issuecomment-4450405931
    view_matrix_numpy = glm.lookat(eye=(0, 0, 4), center=(0, 0, 0), up=(0, 1, 0))
    projection_matrix_numpy = glm.perspective(fovy=45.0, aspect=canvas.get_width() / canvas.get_height(), znear=0.1, zfar=10.0)
    view_matrix = Bufferx.from_numpy(np.array([view_matrix_numpy], dtype=np.float32), BufferType.mat4)
    projection_matrix = Bufferx.from_numpy(np.array([projection_matrix_numpy], dtype=np.float32), BufferType.mat4)
    camera = Camera(view_matrix, projection_matrix)

    # =============================================================================
    # Render
    # =============================================================================

    # Create renderer and render
    renderer_name = ExampleHelper.get_renderer_name()
    renderer_base = ExampleHelper.create_renderer(renderer_name, canvas)

    # =============================================================================
    # Render loop
    # =============================================================================
    def render_static():
        renderer_base.render([viewport], [mesh], [model_matrix], [camera])
        renderer_base.show()

    def render_animated():
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

            scale_x = 1.0
            scale_y = 1.0
            scale_z = 1.0

            matrix_rotation = glm.xrotate(angle_x) @ glm.yrotate(angle_y) @ glm.zrotate(angle_z)
            matrix_translation = glm.translate(np.array([position_x, position_y, position_z]))
            matrix_scale = glm.scale(np.array([scale_x, scale_y, scale_z]))

            matrix_mvp = matrix_translation @ matrix_scale @ matrix_rotation

            model_matrix = Bufferx.from_numpy(np.array([matrix_mvp]), BufferType.mat4)

            # Keep Phong lights anchored in world space as the mesh rotates.
            if material_type == "phong":
                phong_material = mesh.get_material()
                assert isinstance(phong_material, MeshPhongMaterial)
                update_phong_lights_world_fixed(phong_material.get_lights(), matrix_mvp)

            renderer_base.render([viewport], [mesh], [model_matrix], [camera])
            changed_visuals: list[VisualBase] = []
            return changed_visuals

        animator.start()

    animation_enabled = True
    if animation_enabled is False:
        render_static()
    else:
        render_animated()


if __name__ == "__main__":
    main()
