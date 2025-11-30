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

    canvas_width_in = 1
    canvas_height_in = 1
    canvas_width_px = int(canvas_width_in * MY_SCREEN_PPI)
    canvas_height_px = int(canvas_height_in * MY_SCREEN_PPI)

    # Create a canvas
    canvas = Canvas(width=canvas_width_px, height=canvas_height_px, dpi=MY_SCREEN_PPI)

    # Create a viewport and add it to the canvas
    viewport = Viewport(0, 0, canvas.get_width(), canvas.get_height())

    # =============================================================================
    # Render
    # =============================================================================

    matplotlib_renderer = MatplotlibRenderer(canvas)

    # =============================================================================
    # Draw a rectangle in the matplotlib axes to verify size
    # - add text to indicate target size and PPI
    # =============================================================================

    mpl_figure = matplotlib_renderer.get_mpl_figure()
    # Create an axes that fills the whole figure (no margins)
    mpl_axes = mpl_figure.add_axes((0, 0, 1, 1))

    # Draw a rectangle that should fill the exact space
    # (0,0) is bottom left, width=2, height=3
    rect = matplotlib.patches.Rectangle((0, 0), canvas_width_in, canvas_height_in, linewidth=5, edgecolor="r", facecolor="none")

    mpl_axes.add_patch(rect)

    # Set limits to match the size so the coordinates map 1:1 to inches
    mpl_axes.set_xlim(0, canvas_width_in)
    mpl_axes.set_ylim(0, canvas_height_in)

    # Remove ticks/labels for clean visualization
    mpl_axes.axis("off")

    # Add text to verify
    mpl_axes.text(
        canvas_width_in / 2,
        canvas_height_in / 2,
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
