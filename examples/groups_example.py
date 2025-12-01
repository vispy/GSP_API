# stdlib imports
import os
import pathlib

# pip imports
import numpy as np
import matplotlib.pyplot

# local imports
from gsp.core import Canvas, Viewport
from gsp.visuals import Pixels
from gsp.types import Buffer, BufferType
from gsp.core import Camera
from common.example_helper import ExampleHelper
from gsp_extra.bufferx import Bufferx
from gsp.constants import Constants
from gsp.utils.group_utils import GroupUtils


def main():
    # Create a canvas
    canvas = Canvas(100, 100, 20.0)

    # Create a viewport and add it to the canvas
    viewport = Viewport(0, 0, canvas.get_width(), canvas.get_height())

    # =============================================================================
    # Add random points
    # - various ways to create Buffers
    # =============================================================================
    pixel_count = 10_000

    # Random positions - Create buffer from numpy array
    positions_numpy = np.random.rand(pixel_count, 3).astype(np.float32) * 2.0 - 1
    positions_buffer = Bufferx.from_numpy(positions_numpy, BufferType.vec3)

    # define groups
    groups = [
        [i for i in range(len(positions_numpy)) if positions_numpy[i][1] > 0 and positions_numpy[i][0] > 0],
        [i for i in range(len(positions_numpy)) if positions_numpy[i][1] <= 0 and positions_numpy[i][0] > 0],
        [i for i in range(len(positions_numpy)) if positions_numpy[i][1] > 0 and positions_numpy[i][0] <= 0],
        [i for i in range(len(positions_numpy)) if positions_numpy[i][1] <= 0 and positions_numpy[i][0] <= 0],
    ]
    group_count = GroupUtils.get_group_count(pixel_count, groups)

    # all pixels red - Create buffer and fill it with a constant
    colors_buffer = Buffer(group_count, BufferType.rgba8)
    colors_buffer.set_data(Constants.Color.red + Constants.Color.green + Constants.Color.blue + Constants.Color.cyan, 0, 4)

    # Create the Pixels visual and add it to the viewport
    pixels = Pixels(positions_buffer, colors_buffer, groups)
    model_matrix = Bufferx.mat4_identity()

    # =============================================================================
    # Render the canvas
    # =============================================================================

    # Create a camera
    view_matrix = Bufferx.mat4_identity()
    projection_matrix = Buffer(1, BufferType.mat4)
    projection_matrix.set_data(bytearray(np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]], dtype=np.float32).tobytes()), 0, 1)
    camera = Camera(view_matrix, projection_matrix)

    # =============================================================================
    # Render
    # =============================================================================

    # Create renderer and render
    renderer_name = ExampleHelper.get_renderer_name()
    renderer_base = ExampleHelper.create_renderer(renderer_name, canvas)
    rendered_image = renderer_base.render([viewport], [pixels], [model_matrix], [camera])

    # Save to file
    ExampleHelper.save_output_image(rendered_image, f"{pathlib.Path(__file__).stem}_{renderer_name}.png")

    # Show the renderer
    renderer_base.show()


if __name__ == "__main__":
    main()
