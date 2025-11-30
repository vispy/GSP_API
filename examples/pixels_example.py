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
from gsp_extra.bufferx import Bufferx
from gsp.utils.group_utils import GroupUtils
from common.example_helper import ExampleHelper


def main():
    # fix random seed for reproducibility
    np.random.seed(0)

    # Create a canvas
    canvas = Canvas(100, 100, 96.0)

    # Create a viewport and add it to the canvas
    viewport = Viewport(0, 0, canvas.get_width(), canvas.get_height())

    # =============================================================================
    # Add random points
    # - various ways to create Buffers
    # =============================================================================

    point_count = 10_000
    group_size = point_count
    group_count = GroupUtils.get_group_count(point_count, groups=group_size)

    # Random positions - Create buffer from numpy array
    positions_numpy = np.random.rand(point_count, 3).astype(np.float32) * 2.0 - 1
    positions_buffer = Bufferx.from_numpy(positions_numpy, BufferType.vec3)

    # all pixels red - Create buffer and fill it with a constant
    colors_buffer = Buffer(group_count, BufferType.rgba8)
    colors_buffer.set_data(bytearray([255, 0, 0, 255]) * group_count, 0, group_count)

    # Create the Pixels visual and add it to the viewport
    pixels = Pixels(positions_buffer, colors_buffer, groups=group_size)

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
    rendered_image = renderer_base.render([viewport], [pixels], [model_matrix], [camera])

    # Save to file
    image_basename = f"{pathlib.Path(__file__).stem}_{renderer_name}.png"
    image_path = pathlib.Path(__file__).parent / "output" / image_basename
    with open(image_path, "wb") as file_writer:
        file_writer.write(rendered_image)
    print(f"Rendered image saved to: {image_path}")


if __name__ == "__main__":
    main()
