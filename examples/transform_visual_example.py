# stdlib imports
import os
import pathlib

# pip imports
import numpy as np
import matplotlib.pyplot


# local imports
from gsp.core import Canvas, Viewport, Camera
from gsp.visuals import Pixels
from gsp.constants import Constants
from gsp.types import Buffer, BufferType
from gsp.transforms import TransformChain
from gsp_extra.bufferx import Bufferx
from gsp.transforms.links.transform_link_immediate import TransformLinkImmediate
from gsp.utils import GroupUtils
from common.example_helper import ExampleHelper
from gsp_extra.transform_links.transform_load import TransformLoad


def main():
    # Create a canvas
    canvas = Canvas(100, 100, 96.0)

    # Create a viewport and add it to the canvas
    viewport = Viewport(0, 0, canvas.get_width(), canvas.get_height())

    # =============================================================================
    # Add random points
    # - various ways to create Buffers
    # =============================================================================
    point_count = 10_000

    # Random positions - Create buffer from numpy array
    positions_numpy = np.random.rand(point_count, 3).astype(np.float32) * 2.0 - 1
    positions_buffer = Bufferx.from_numpy(positions_numpy, BufferType.vec3)

    # positions_transform = TransformChain(buffer_count=-1, buffer_type=BufferType.vec3)
    # positions_uri = f"file://{pathlib.Path(__file__).parent.resolve()}/images/UV_Grid_Sm.jpg"
    # positions_transform.add(TransformLoad(positions_uri, BufferType.vec3))

    # define groups
    groups = [
        [i for i in range(len(positions_numpy)) if positions_numpy[i][1] > 0],
        [i for i in range(len(positions_numpy)) if positions_numpy[i][1] <= 0],
    ]
    group_count = GroupUtils.get_group_count(point_count, groups)

    # all pixels red - Create buffer and fill it with a constant
    colors_buffer = Buffer(group_count, BufferType.rgba8)
    colors_buffer.set_data(Constants.Color.red + Constants.Color.green, 0, 2)
    colors_transform = TransformChain(buffer_count=group_count, buffer_type=BufferType.rgba8)
    colors_transform.add(TransformLinkImmediate(colors_buffer))

    # Create the Pixels visual and add it to the viewport
    pixels = Pixels(positions_buffer, colors_transform, groups)
    model_matrix = Bufferx.mat4_identity()

    # =============================================================================
    # Render the canvas
    # =============================================================================

    # Create a camera
    view_matrix = Bufferx.mat4_identity()
    projection_matrix = Bufferx.mat4_identity()
    camera = Camera(view_matrix, projection_matrix)

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
