"""Example showing how to render multiple viewports on a single canvas."""

# stdlib imports
import pathlib

# pip imports
import numpy as np

# local imports
from gsp.constants import Constants
from gsp.core import Canvas, Viewport
from gsp.visuals import Pixels
from gsp.visuals import Points
from gsp.types import Buffer, BufferType
from gsp.core import Camera
from gsp_extra.bufferx import Bufferx
from gsp.utils.group_utils import GroupUtils
from common.example_helper import ExampleHelper
from gsp.utils.unit_utils import UnitUtils


def main():
    """Main function for the viewport multi example."""
    # fix random seed for reproducibility
    np.random.seed(0)

    # Create a canvas
    canvas = Canvas(100, 100, 96.0)

    half_width = int(canvas.get_width() / 2)
    half_height = int(canvas.get_height() / 2)

    # Create viewports
    viewport_1 = Viewport(0, 0, int(half_width * 3.0 / 2.0), int(half_height * 2.0))
    viewport_2 = Viewport(int(half_width * 1.0 / 2.0), 0, int(half_width * 3.0 / 2.0), int(half_height * 2.0))

    # =============================================================================
    # Add random points
    # - various ways to create Buffers
    # =============================================================================

    def generate_points(gsp_color: bytearray) -> Points:
        point_count = 50
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

        # Sizes - Create buffer and set data with numpy array
        sizes_numpy = np.array([40] * point_count, dtype=np.float32)
        sizes_buffer = Bufferx.from_numpy(sizes_numpy, BufferType.float32)

        # all pixels red - Create buffer and fill it with a constant
        face_colors_buffer = Buffer(point_count, BufferType.rgba8)
        face_colors_buffer.set_data(gsp_color * point_count, 0, point_count)

        # Edge colors - Create buffer and fill it with a constant
        edge_colors_buffer = Buffer(point_count, BufferType.rgba8)
        edge_colors_buffer.set_data(Constants.Color.blue * point_count, 0, point_count)

        # Edge widths - Create buffer and fill it with a constant
        edge_widths_numpy = np.array([UnitUtils.pixel_to_point(1, canvas.get_dpi())] * point_count, dtype=np.float32)
        edge_widths_buffer = Bufferx.from_numpy(edge_widths_numpy, BufferType.float32)

        # Create the Points visual and add it to the viewport
        points = Points(positions_buffer, sizes_buffer, face_colors_buffer, edge_colors_buffer, edge_widths_buffer)
        return points

    pixels_1 = generate_points(gsp_color=Constants.Color.red)
    pixels_2 = generate_points(gsp_color=Constants.Color.green)
    model_matrix = Bufferx.mat4_identity()

    # =============================================================================
    # Render the canvas
    # =============================================================================

    # Create a camera
    camera = Camera(Bufferx.mat4_identity(), Bufferx.mat4_identity())

    # =============================================================================
    # Render
    # =============================================================================

    # Create renderer and render
    renderer_name = ExampleHelper.get_renderer_name()
    renderer_base = ExampleHelper.create_renderer(renderer_name, canvas)
    rendered_image = renderer_base.render([viewport_1, viewport_2], [pixels_1, pixels_2], [model_matrix, model_matrix], [camera, camera])

    # Save to file
    ExampleHelper.save_output_image(rendered_image, f"{pathlib.Path(__file__).stem}_{renderer_name}.png")

    # Show the renderer
    renderer_base.show()


if __name__ == "__main__":
    main()
