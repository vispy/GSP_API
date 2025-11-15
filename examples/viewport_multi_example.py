# stdlib imports
import os

# pip imports
import numpy as np
import matplotlib.pyplot

# local imports
from gsp.constants import Constants
from gsp.core import Canvas, Viewport
from gsp.visuals import Pixels
from gsp.types import Buffer, BufferType
from gsp.core import Camera
from gsp_matplotlib.renderer import MatplotlibRenderer
from gsp_datoviz.renderer import DatovizRenderer
from gsp_extra.bufferx import Bufferx
from gsp.utils.group_utils import GroupUtils


def main():
    # fix random seed for reproducibility
    np.random.seed(0)

    # Create a canvas
    canvas = Canvas(100, 100, 96.0)

    half_width = int(canvas.get_width() / 2)
    half_height = int(canvas.get_height() / 2)

    # Create viewports
    viewport_1 = Viewport(0, 0, half_width, half_height)
    viewport_2 = Viewport(half_width, 0, half_width, half_height)
    viewport_3 = Viewport(0, half_height, half_width, half_height)
    viewport_4 = Viewport(half_width, half_height, half_width, half_height)

    # =============================================================================
    # Add random points
    # - various ways to create Buffers
    # =============================================================================

    def generate_pixels(gsp_color: bytearray) -> Pixels:
        point_count = 1_000
        group_size = point_count
        group_count = GroupUtils.get_group_count(point_count, groups=group_size)

        # Random positions - Create buffer from numpy array
        positions_angle = np.linspace(0, 4 * np.pi, point_count)
        positions_radius = np.linspace(0.0, 1.0, point_count)
        positions_x = positions_radius * np.sin(positions_angle)
        positions_y = positions_radius * np.cos(positions_angle)
        positions_z = np.zeros(point_count)
        positions_numpy = np.vstack((positions_x, positions_y, positions_z)).T.astype(np.float32)
        positions_buffer = Bufferx.from_numpy(positions_numpy, BufferType.vec3)

        # all pixels red - Create buffer and fill it with a constant
        colors_buffer = Buffer(group_count, BufferType.rgba8)
        colors_buffer.set_data(gsp_color * group_count, 0, group_count)

        # Create the Pixels visual and add it to the viewport
        pixels = Pixels(positions_buffer, colors_buffer, groups=group_size)
        return pixels

    pixels_1 = generate_pixels(gsp_color=Constants.Color.red)
    pixels_2 = generate_pixels(gsp_color=Constants.Color.green)
    model_matrix = Bufferx.mat4_identity()

    # =============================================================================
    # Render the canvas
    # =============================================================================

    # Create a camera
    camera = Camera(Bufferx.mat4_identity(), Bufferx.mat4_identity())

    # =============================================================================
    # Render
    # =============================================================================

    # Create a renderer and render the scene
    renderer = MatplotlibRenderer(canvas) if os.environ.get("GSP_RENDERER", "matplotlib") == "matplotlib" else DatovizRenderer(canvas)
    renderer.render(
        [viewport_1, viewport_2, viewport_3, viewport_4],
        [pixels_1, pixels_2, pixels_2, pixels_1],
        [model_matrix, model_matrix, model_matrix, model_matrix],
        [camera, camera, camera, camera],
    )
    renderer.show()


if __name__ == "__main__":
    main()
