"""Example demonstrating the AxesDisplay with pan and zoom functionality."""

# pip imports
import numpy as np

# local imports
from common.example_helper import ExampleHelper
from gsp.core import Canvas
from gsp_extra.bufferx import Bufferx
from gsp.types import BufferType, VisualBase, MarkerShape
import vispy_2 as Vispy2


def main():
    """Main function to run the example."""
    # fix random seed for reproducibility
    np.random.seed(0)

    # Create a canvas
    canvas = Canvas(width=400, height=400, dpi=127)

    # Create a renderer
    renderer_name = ExampleHelper.get_renderer_name()
    renderer_base = ExampleHelper.create_renderer(renderer_name, canvas)

    # =============================================================================
    #
    # =============================================================================

    # Create an AxesManaged instance for the canvas
    axes_managed = Vispy2.axes.AxesManaged(renderer_base, 40, 40, 320, 320)

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

        # positions_numpy = np.random.rand(point_count, 3).astype(np.float32) * 2.0 - 1
        positions_buffer = Bufferx.from_numpy(positions_numpy, BufferType.vec3)

        # Create the Points visual and add it to the viewport
        points = Vispy2.scatter(positions_buffer, marker_shape=MarkerShape.club)
        return points

    points = generate_visual_points(100)

    axes_managed.add_visual(points)

    # =============================================================================
    #
    # =============================================================================

    # start the animation loop
    axes_managed.start()


if __name__ == "__main__":
    main()
