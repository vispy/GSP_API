"""Example demonstrating the AxesDisplay with pan and zoom functionality."""

# pip imports
import numpy as np

# local imports
from common.example_helper import ExampleHelper
from gsp.core import Canvas, Viewport
from gsp.core.camera import Camera
from gsp.visuals import Points
from gsp_extra.bufferx import Bufferx
from gsp.types import BufferType
from gsp.types import Buffer
from gsp.constants import Constants
from gsp.utils.unit_utils import UnitUtils
from gsp_extra.misc.render_item import RenderItem
from vispy2.axes.axes_managed import AxesManaged
from gsp.utils.renderer_registery import RendererRegistry

from gsp_matplotlib import register_renderer_matplotlib
from gsp_network import register_renderer_network
from gsp_datoviz import register_renderer_datoviz


def main():
    """Main function to run the example."""
    # fix random seed for reproducibility
    np.random.seed(0)

    # Create a canvas
    canvas = Canvas(width=400, height=400, dpi=127)

    renderer_name = ExampleHelper.get_renderer_name()
    renderer_base = ExampleHelper.create_renderer(renderer_name, canvas)

    # =============================================================================
    #
    # =============================================================================

    # Create an AxesManaged instance for the canvas with a viewport that takes 80% of the canvas size and is centered
    viewport_x = int(canvas.get_width() * 0.1)
    viewport_y = int(canvas.get_height() * 0.1)
    viewport_width = int(canvas.get_width() * 0.8)
    viewport_height = int(canvas.get_height() * 0.8)

    axes_managed = AxesManaged(renderer_base, viewport_x, viewport_y, viewport_width, viewport_height)

    # =============================================================================
    #
    # =============================================================================

    def generate_visual_points(point_count: int, viewport: Viewport) -> RenderItem:
        # Generate a sinusoidal distribution of points
        sin_scale = 3.0
        x_values = np.linspace(-1.0, +1.0, point_count, dtype=np.float32)
        y_values = np.sin(x_values * np.pi * sin_scale).astype(np.float32)
        z_values = np.zeros(point_count, dtype=np.float32)
        positions_numpy = np.vstack((x_values, y_values, z_values)).T.astype(np.float32)

        # positions_numpy = np.random.rand(point_count, 3).astype(np.float32) * 2.0 - 1
        positions_buffer = Bufferx.from_numpy(positions_numpy, BufferType.vec3)

        # Sizes - Create buffer and set data with numpy array
        sizes_numpy = np.array([10] * point_count, dtype=np.float32)
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

        # Create model matrix to transform points into axes data space
        model_matrix = Bufferx.mat4_identity()

        camera = Camera(Bufferx.mat4_identity(), Bufferx.mat4_identity())

        render_item = RenderItem(viewport, points, model_matrix, camera)
        return render_item

    render_item_points = generate_visual_points(100, axes_managed.get_viewport())

    axes_managed.add_render_items(render_item_points)

    # =============================================================================
    #
    # =============================================================================

    # start the animation loop
    axes_managed.get_animator().start([], [], [], [])


if __name__ == "__main__":
    main()
