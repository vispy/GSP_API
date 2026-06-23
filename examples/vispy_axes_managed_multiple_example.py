"""Example demonstrating the AxesDisplay with pan and zoom functionality."""

# pip imports
import numpy as np

# local imports
from common.example_helper import ExampleHelper
from gsp.core import Canvas
from gsp.types import Buffer, BufferType, VisualBase
from gsp.constants import Constants
from gsp.utils.unit_utils import UnitUtils
from gsp.visuals import Points
from gsp_extra.bufferx import Bufferx
import vispy2 as Vispy2


def main():
    """Main function to run the example."""
    # fix random seed for reproducibility
    np.random.seed(0)

    # Create a canvas
    canvas = Canvas(width=400, height=400, dpi=127, background_color=Constants.Color.transparent)

    # Create a renderer
    renderer_name = ExampleHelper.get_renderer_name()
    renderer_base = ExampleHelper.create_renderer(renderer_name, canvas)
    animator_base = ExampleHelper.create_animator(renderer_base)

    # =============================================================================
    #
    # =============================================================================

    # @animator_base.event_listener
    # def animator_callback(delta_time: float) -> list[VisualBase]:
    #     """Animator callback to handle rendering frequency."""
    #     renderer_base.clear()  # Clear the canvas before rendering the next frame

    #     changed_visuals: list[VisualBase] = []
    #     return changed_visuals

    # Create an AxesManaged instance for the canvas
    axes_managed1 = Vispy2.axes.AxesManaged(renderer_base, 40, 40, 160, 160, animator_base=animator_base)
    axes_managed2 = Vispy2.axes.AxesManaged(renderer_base, 240, 40, 160, 160, animator_base=animator_base)
    axes_managed3 = Vispy2.axes.AxesManaged(renderer_base, 40, 240, 160, 160, animator_base=animator_base)
    axes_managed4 = Vispy2.axes.AxesManaged(renderer_base, 240, 240, 160, 160, animator_base=animator_base)

    # =============================================================================
    #
    # =============================================================================

    def generate_visual_points(point_count: int) -> VisualBase:
        # Generate a sinusoidal distribution of points
        sin_scale = 3.0
        x_values = np.linspace(-1.0, +1.0, point_count, dtype=np.float32)
        y_values = np.sin(x_values * np.pi * sin_scale).astype(np.float32)
        z_values = np.zeros(point_count, dtype=np.float32)
        positions_numpy = np.vstack((x_values, y_values, z_values)).T.astype(np.float32)

        positions_buffer = Bufferx.from_numpy(positions_numpy, BufferType.vec3)
        sizes_buffer = Bufferx.from_numpy(np.array([10] * point_count, dtype=np.float32), BufferType.float32)
        face_colors_buffer = Buffer(point_count, BufferType.rgba8)
        face_colors_buffer.set_data(bytearray([255, 0, 0, 255]) * point_count, 0, point_count)
        edge_colors_buffer = Buffer(point_count, BufferType.rgba8)
        edge_colors_buffer.set_data(Constants.Color.blue * point_count, 0, point_count)
        edge_widths_numpy = np.array([UnitUtils.pixel_to_point(1, canvas.get_dpi())] * point_count, dtype=np.float32)
        edge_widths_buffer = Bufferx.from_numpy(edge_widths_numpy, BufferType.float32)
        points = Points(positions_buffer, sizes_buffer, face_colors_buffer, edge_colors_buffer, edge_widths_buffer)
        return points

    points = generate_visual_points(100)

    axes_managed1.add_visual(points)
    axes_managed2.add_visual(points)
    axes_managed3.add_visual(points)
    axes_managed4.add_visual(points)

    # =============================================================================
    #
    # =============================================================================

    # start the animation loop
    animator_base.start()


if __name__ == "__main__":
    main()
