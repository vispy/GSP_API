"""Example rendering a mesh with MeshTexturedMaterial (UV texture + Phong lighting)."""

# stdlib imports
import pathlib
from typing import Sequence

# pip imports
import numpy as np

# local imports
from gsp.core import Canvas, Viewport, Camera
from gsp.lights.ambient_light import AmbientLight
from gsp.lights.directional_light import DirectionalLight
from gsp.lights.light import Light
from gsp.materials.mesh_textured_material import MeshTexturedMaterial
from gsp.types.visual_base import VisualBase
from gsp.visuals.mesh import Mesh
from gsp.types import Buffer, BufferType
from gsp_extra.bufferx import Bufferx
from gsp_extra.misc.mesh_utils import MeshUtils
from gsp_extra.misc.texture_utils import TextureUtils
from gsp.constants import Constants
from common.example_helper import ExampleHelper
from gsp_extra.mpl3d import glm

# Intended world-space positions for the directional light.
PHONG_DIRECTIONAL_LIGHT_WORLD_POSITION = np.array([5.0, 5.0, 5.0], dtype=np.float32)
PHONG_DIRECTIONAL_TARGET_WORLD_POSITION = np.array([0.0, 0.0, 0.0], dtype=np.float32)


def create_phong_lights() -> Sequence[Light]:
    """Build a small default light scene: one ambient + one directional."""
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
    """Anchor each light at its world-space position even as the mesh's model_matrix changes."""
    inverse_model = np.linalg.inv(model_matrix_numpy)

    def to_model_space_buffer(world_position: np.ndarray) -> Buffer:
        world_homogeneous = np.append(world_position, 1.0)
        model_xyz = (inverse_model @ world_homogeneous)[:3].astype(np.float32)
        return Bufferx.from_numpy(model_xyz.reshape(1, 3), BufferType.vec3)

    for light in lights:
        if isinstance(light, DirectionalLight):
            light.set_light_position(to_model_space_buffer(PHONG_DIRECTIONAL_LIGHT_WORLD_POSITION))
            light.set_target_position(to_model_space_buffer(PHONG_DIRECTIONAL_TARGET_WORLD_POSITION))


def main():
    """Example rendering a mesh with MeshTexturedMaterial (UV texture + Phong lighting)."""
    np.random.seed(0)

    canvas = Canvas(400, 400, 72.0, Constants.Color.white)
    viewport = Viewport(0, 0, canvas.get_width(), canvas.get_height(), Constants.Color.transparent)

    obj_path = pathlib.Path(__file__).parent / "models" / "suzanne.obj"
    mesh_geometry = MeshUtils.parse_obj_file_manual(str(obj_path))

    texture_path = pathlib.Path(__file__).parent / "images" / "UV_Grid_Sm.jpg"
    texture = TextureUtils.load_image(str(texture_path))

    color = Bufferx.from_numpy(np.array([Constants.Color.white], dtype=np.uint8), BufferType.rgba8)
    specular_color = Bufferx.from_numpy(np.array([[255, 255, 255, 255]], dtype=np.uint8), BufferType.rgba8)
    lights = create_phong_lights()
    mesh_material = MeshTexturedMaterial(
        texture,
        color,
        specular_color,
        32.0,
        lights,
        True,
        Constants.FaceCulling.FrontSide,
    )

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

        textured_material = mesh.get_material()
        assert isinstance(textured_material, MeshTexturedMaterial)
        update_phong_lights_world_fixed(textured_material.get_lights(), matrix_mvp)

        renderer_base.render([viewport], [mesh], [model_matrix], [camera])
        return []

    animator.start()


if __name__ == "__main__":
    main()
