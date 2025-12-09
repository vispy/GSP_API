# stdlib imports
import os
import pathlib
from typing import Literal
import typing

# pip imports
import numpy as np

# local imports
from common.example_helper import ExampleHelper
from gsp.constants import Constants
from gsp.core import Canvas, Viewport
from gsp.visuals import Texts
from gsp.types import Buffer, BufferType
from gsp.core import Camera
from gsp_extra.bufferx import Bufferx
from gsp.utils.unit_utils import UnitUtils


def main():
    # fix random seed for reproducibility
    np.random.seed(0)

    # Create a canvas
    canvas = Canvas(width=256, height=256, dpi=127.5)

    # Create a viewport and add it to the canvas
    viewport = Viewport(0, 0, canvas.get_width(), canvas.get_height())

    # =============================================================================
    # Add random points
    # - various ways to create Buffers
    # =============================================================================
    point_count = 2

    # Random positions - Create buffer from numpy array
    positions_numpy = np.array([[-0.5, 0.0, 0.0], [0.5, 0.0, 0.0]], dtype=np.float32)
    positions_buffer = Bufferx.from_numpy(positions_numpy, BufferType.vec3)

    texts_content: list[str] = ["Hello", "World"]

    # colors - Create buffer and fill it with a constant
    colors_buffer = Buffer(point_count, BufferType.rgba8)
    colors_buffer.set_data(Constants.Color.red + Constants.Color.green, 0, point_count)

    font_size_numpy = np.array([12, 12], dtype=np.float32)
    font_size_buffer = Bufferx.from_numpy(font_size_numpy, BufferType.float32)

    anchors_numpy = np.array([[0.0, 1.0], [0.0, 1.0]], dtype=np.float32)
    anchors_buffer = Bufferx.from_numpy(anchors_numpy, BufferType.vec2)

    angles_numpy = np.array([+45, -45], dtype=np.float32)
    angles_buffer = Bufferx.from_numpy(angles_numpy, BufferType.float32)

    font_name = "Arial"

    # Create the Texts visual
    texts = Texts(positions_buffer, texts_content, colors_buffer, font_size_buffer, anchors_buffer, angles_buffer, font_name)

    # =============================================================================
    # Render the canvas
    # =============================================================================

    model_matrix = Bufferx.mat4_identity()
    # Create a camera
    camera = Camera(Bufferx.mat4_identity(), Bufferx.mat4_identity())

    # =============================================================================
    # Render
    # =============================================================================

    # Create renderer and render
    renderer_name = ExampleHelper.get_renderer_name()
    renderer_base = ExampleHelper.create_renderer(renderer_name, canvas)
    rendered_image = renderer_base.render([viewport], [texts], [model_matrix], [camera])

    # Save to file
    ExampleHelper.save_output_image(rendered_image, f"{pathlib.Path(__file__).stem}_{renderer_name}.png")

    # Show the renderer
    renderer_base.show()


if __name__ == "__main__":
    main()
