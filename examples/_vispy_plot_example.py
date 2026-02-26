"""Scatter example demonstrating the use of the scatter function to create different types of visuals.

- Left: Pixels visual with random positions and red color.
- Right: Markers visual with random positions, varying sizes and colors.
"""

# stdlib imports
import pathlib

# pip imports
import numpy as np

# local imports
from gsp.core import Canvas, Viewport
from gsp.types import Buffer, BufferType, VisualBase, MarkerShape
from gsp.core import Camera
from gsp_extra.bufferx import Bufferx
from gsp.utils.group_utils import GroupUtils
from gsp.utils.cmap_utils import CmapUtils
from gsp.constants import Constants

from gsp_extra.misc.render_item import RenderItem
from common.example_helper import ExampleHelper

# from vispy_2 import scatter
from gsp_nico import viewport
import vispy2 as Vispy2
from vispy2.axes import axes_managed


def main():
    """Main function for the scatter example."""
    # fix random seed for reproducibility
    np.random.seed(0)

    # Create a canvas
    canvas = Canvas(400, 400, 72.0)

    # Create a renderer
    renderer_name = ExampleHelper.get_renderer_name()
    renderer_base = ExampleHelper.create_renderer(renderer_name, canvas)

    # Create an AxesManaged instance for the canvas
    axes_managed = Vispy2.axes.AxesManaged(renderer_base, 40, 40, 320, 320)

    axes_managed.get_axes_display().set_limits_dunit(-1, 11, -3, 3)

    # =============================================================================
    # Add random points
    # - various ways to create Buffers
    # =============================================================================

    def createVisualPoints() -> list[VisualBase]:
        point_count = 20

        # Create Buffers
        x_numpy = np.linspace(0, 10, point_count, dtype=np.float32).reshape(point_count, 1)
        x_buffer = Bufferx.from_numpy(x_numpy, BufferType.float32)

        y_numpy = np.sin(x_numpy).astype(np.float32)
        y_buffer = Bufferx.from_numpy(y_numpy, BufferType.float32)

        # Create the Points visual and add it to the viewport
        visuals = Vispy2.plot(
            x_buffer,
            y_buffer,
            fmt="bo",
        )
        return visuals

    visuals = createVisualPoints()

    # =============================================================================
    # Render
    # =============================================================================

    for visual in visuals:
        axes_managed.add_visual(visual)

    # start the animation loop
    axes_managed.start()


if __name__ == "__main__":
    main()
