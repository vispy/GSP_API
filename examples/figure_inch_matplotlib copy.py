# stdlib imports
import os
from typing import Literal
import typing

# pip imports
import numpy as np
import matplotlib.patches
from PyQt5.QtWidgets import QApplication

# local imports
from common.example_helper import ExampleHelper
from gsp.constants import Constants
from gsp.core import Canvas, Viewport
from gsp.visuals import Points
from gsp.types import Buffer, BufferType
from gsp.core import Camera
from gsp_extra.bufferx import Bufferx
from gsp.utils.unit_utils import UnitUtils
from gsp_matplotlib.renderer import MatplotlibRenderer

from gsp.utils.group_utils import GroupUtils
from gsp.visuals import Pixels


class QtHelper:
    """Get screen properties via Qt"""

    @staticmethod
    def get_screen_ppi() -> float:

        qt_app = QApplication([])
        screen = qt_app.primaryScreen()
        assert screen is not None, "screen MUST NOT be None"
        screen_ppi = screen.physicalDotsPerInch()
        qt_app.quit()
        return screen_ppi

    @staticmethod
    def get_device_pixel_ratio() -> float:
        qt_app = QApplication([])
        screen = qt_app.primaryScreen()
        assert screen is not None, "screen MUST NOT be None"
        device_pixel_ratio = screen.devicePixelRatio()
        qt_app.quit()
        return device_pixel_ratio


def main():
    # fix random seed for reproducibility
    np.random.seed(0)

    # INPUT: Update this value based on your hardware (see table above)
    # This is the crucial link between software points and hardware reality.
    MY_SCREEN_PPI = QtHelper.get_screen_ppi()

    canvas_width_in = 5
    canvas_height_in = 5
    canvas_width_px = int(canvas_width_in * MY_SCREEN_PPI)
    canvas_height_px = int(canvas_height_in * MY_SCREEN_PPI)

    # Create a canvas
    canvas = Canvas(width=canvas_width_px, height=canvas_height_px, dpi=MY_SCREEN_PPI)

    # Create a viewport and add it to the canvas
    viewport = Viewport(0, 0, canvas.get_width(), canvas.get_height())
    # =============================================================================
    # Add transparent points
    # - various ways to create Buffers
    # =============================================================================

    point_count = 1
    group_size = point_count
    group_count = GroupUtils.get_group_count(point_count, groups=group_size)

    # Random positions - Create buffer from numpy array
    positions_numpy = np.random.rand(point_count, 3).astype(np.float32) * 2.0 - 1
    positions_buffer = Bufferx.from_numpy(positions_numpy, BufferType.vec3)

    # all pixels red - Create buffer and fill it with a constant
    colors_buffer = Buffer(group_count, BufferType.rgba8)
    colors_buffer.set_data(Constants.Color.transparent * group_count, 0, group_count)

    # Create the Pixels visual and add it to the viewport
    pixels = Pixels(positions_buffer, colors_buffer, groups=group_size)

    # =============================================================================
    # Render the canvas
    # =============================================================================

    model_matrix = Bufferx.mat4_identity()
    # Create a camera
    camera = Camera(Bufferx.mat4_identity(), Bufferx.mat4_identity())

    # =============================================================================
    # Render
    # =============================================================================

    matplotlib_renderer = MatplotlibRenderer(canvas)

    # Fake render just to setup a viewport
    matplotlib_renderer.render([viewport], [pixels], [model_matrix], [camera])

    # =============================================================================
    # Draw a rectangle in the matplotlib axes to verify size
    # - add text to indicate target size and PPI
    # =============================================================================

    mpl_axes = matplotlib_renderer.get_mpl_axes_for_viewport(viewport)
    # Draw a rectangle that should fill the exact space
    mpl_rectangle = matplotlib.patches.Rectangle((-1, -1), 2, 2, linewidth=5, edgecolor="r", facecolor="none")
    mpl_axes.add_patch(mpl_rectangle)

    # Add text to verify
    mpl_axes.text(
        0,
        0,
        f'Target: {canvas_width_in}" x {canvas_height_in}"\n' f"PPI Set: {MY_SCREEN_PPI}",
        horizontalalignment="center",
        verticalalignment="center",
        fontsize=12,
    )

    # =============================================================================
    #
    # =============================================================================

    matplotlib_renderer.show()


if __name__ == "__main__":
    main()
