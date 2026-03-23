"""Example showing how to use the Pixels visual to render a set of points."""

# stdlib imports
import pathlib
import os

# pip imports
import numpy as np

# local imports
from gsp.core import Canvas, Viewport
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
    obj_path = pathlib.Path(__file__).parent / "models" / "suzanne.obj"
    mesh_geometry = MeshUtils.parse_obj_file_manual(str(obj_path))

    mesh_material = MeshBasicMaterial()
    mesh_material.colors = np.array([255, 0, 255, 255], dtype=np.float32)  # red, green, blue

    # Create a mesh
    mesh = Mesh(mesh_geometry, mesh_material)

    # =============================================================================
    # Render the canvas
    # =============================================================================

    # Model matrix
    model_matrix = Bufferx.mat4_identity()

    # Create a camera
    camera = Camera(Bufferx.mat4_identity(), Bufferx.mat4_identity())

    # =============================================================================
    # Render
    # =============================================================================

    # Create renderer and render
    renderer_name = ExampleHelper.get_renderer_name()
    renderer_base = ExampleHelper.create_renderer(renderer_name, canvas)
    rendered_image = renderer_base.render([viewport], [mesh], [model_matrix], [camera])

    # Save to file
    ExampleHelper.save_output_image(rendered_image, f"{pathlib.Path(__file__).stem}_{renderer_name}.png")

    # Show the renderer
    renderer_base.show()


if __name__ == "__main__":
    main()
