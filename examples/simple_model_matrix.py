"""Example showing how to use a model matrix to transform a visual."""

# stdlib imports
import os
import pathlib

# pip imports
import numpy as np
import matplotlib.pyplot

# local imports
from gsp.core import Canvas, Viewport
from gsp.types import Buffer, BufferType
from gsp.core import Camera
from gsp_extra.bufferx import Bufferx
from gsp.visuals import Points
from gsp.constants import Constants
from gsp.utils.unit_utils import UnitUtils
from gsp_extra.mpl3d import glm
from common.example_helper import ExampleHelper


def main():
    """Main function to run the example."""
    # Create a canvas
    canvas = Canvas(100, 100, 72.0)

    # Create a viewport and add it to the canvas
    viewport = Viewport(0, 0, canvas.get_width(), canvas.get_height())

    # =============================================================================
    # Add random points
    # - various ways to create Buffers
    # =============================================================================
    point_count = 10

    positions_numpy = np.zeros((point_count, 3), dtype=np.float32)

    # Make a line from -0.9 to 0.9 in x
    positions_numpy[:, 0] = np.linspace(-0.9, 0.9, point_count)
    positions_numpy[:, 1] = 0.0
    positions_numpy[:, 2] = -5.0

    # Random positions - Create buffer from numpy array
    positions_buffer = Bufferx.from_numpy(positions_numpy, BufferType.vec3)

    # Sizes - Create buffer and set data with numpy array
    sizes_numpy = np.array([40] * point_count, dtype=np.float32)
    sizes_buffer = Bufferx.from_numpy(sizes_numpy, BufferType.float32)

    # all pixels red - Create buffer and fill it with a constant
    face_colors_buffer = Buffer(point_count, BufferType.rgba8)
    face_colors_buffer.set_data(bytearray([255, 0, 0, 255]) * point_count, 0, point_count)

    # Edge colors - Create buffer and fill it with a constant
    edge_colors_buffer = Buffer(point_count, BufferType.rgba8)
    edge_colors_buffer.set_data(Constants.Color.blue * point_count, 0, point_count)

    # Edge widths - Create buffer and fill it with a constant
    edge_widths_numpy = np.array([UnitUtils.pixel_to_point(1, canvas.get_dpi())] * point_count, dtype=np.float32)
    edge_widths_buffer = Bufferx.from_numpy(edge_widths_numpy, BufferType.float32)

    # Create the Points visual and add it to the viewport
    points = Points(positions_buffer, sizes_buffer, face_colors_buffer, edge_colors_buffer, edge_widths_buffer)

    # =============================================================================
    # Create a model matrix which perform a rotation of 20degree around z
    # =============================================================================

    model_matrix_numpy = glm.zrotate(20.0)
    # axes_transform_numpy = glm.translate(np.array([0.0, 0.0, 0.0])) @ glm.scale(np.array([0.5, 2, 0.5]))
    # model_matrix_numpy = axes_transform_numpy @ model_matrix_numpy
    model_matrix = Bufferx.from_numpy(np.array([model_matrix_numpy]), BufferType.mat4)

    # =============================================================================
    # Render the canvas
    # =============================================================================

    # Create a camera
    camera = Camera(Bufferx.mat4_identity(), Bufferx.mat4_identity())

    # Create renderer and render
    renderer_name = ExampleHelper.get_renderer_name()
    renderer_base = ExampleHelper.create_renderer(renderer_name, canvas)
    rendered_image = renderer_base.render([viewport], [points], [model_matrix], [camera])

    # Save to file
    ExampleHelper.save_output_image(rendered_image, f"{pathlib.Path(__file__).stem}_{renderer_name}.png")

    # Show the renderer
    renderer_base.show()


if __name__ == "__main__":
    main()
