# stdlib imports
import os

# pip imports
import numpy as np

# local imports
from gsp.core import Canvas, Viewport
from gsp.visuals import Segments
from gsp.types import Buffer, BufferType, CapStyle, JoinStyle
from gsp.core import Camera
from gsp_matplotlib.renderer import MatplotlibRenderer
from gsp_datoviz.renderer import DatovizRenderer
from gsp_extra.bufferx import Bufferx
from gsp.utils.cmap_utils import CmapUtils


def main():
    # fix random seed for reproducibility
    np.random.seed(0)

    # Create a canvas
    canvas = Canvas(512, 512, 72.0)

    # Create a viewport and add it to the canvas
    viewport = Viewport(0, 0, canvas.get_width(), canvas.get_height())

    # =============================================================================
    # Generate data
    # =============================================================================

    def generate_data(line_count: int, line_width_max: float, color_map_name: str):
        margin_x = 0.1
        x = np.linspace(-1 + margin_x, 1 - margin_x, line_count).astype(np.float32) * 0.9

        # Create a numpy array `positions` with the shape (line_count, 2, 3)
        # [:, 0, :] -> initial points
        # [:, 1, :] -> terminal points
        positions_numpy = np.zeros((line_count, 2, 3), dtype=np.float32)
        positions_numpy[:, 0, 0] = x  # initial x
        positions_numpy[:, 0, 1] = -0.5  # initial y
        positions_numpy[:, 0, 2] = 0  # initial z
        positions_numpy[:, 1, 0] = x  # terminal x
        positions_numpy[:, 1, 1] = +0.5  # terminal y
        positions_numpy[:, 1, 2] = 0  # terminal z
        positions_buffer = Bufferx.from_numpy(positions_numpy.reshape(-1, 3), BufferType.vec3)

        line_widths_numpy = np.linspace(1, line_width_max, line_count).astype(np.float32)
        line_widths_buffer = Bufferx.from_numpy(line_widths_numpy.reshape(-1, 1), BufferType.float32)

        colors_cursor = np.linspace(0, 1, line_count).astype(np.float32)
        colors_numpy = CmapUtils.get_color_map_numpy(color_map_name, colors_cursor)
        colors_buffer = Bufferx.from_numpy(colors_numpy, BufferType.rgba8)

        return positions_buffer, colors_buffer, line_widths_buffer

    positions_buffer, colors_buffer, line_widths_buffer = generate_data(line_count=10, line_width_max=30.0, color_map_name="plasma")

    # =============================================================================
    #
    # =============================================================================

    # Create the Pixels visual and add it to the viewport
    segments = Segments(positions_buffer, line_widths_buffer, CapStyle.ROUND, colors_buffer)
    model_matrix = Bufferx.mat4_identity()

    # =============================================================================
    # Render the canvas
    # =============================================================================

    # Create a camera
    view_matrix = Bufferx.mat4_identity()
    projection_matrix = Bufferx.mat4_identity()
    camera = Camera(view_matrix, projection_matrix)

    # =============================================================================
    # Render
    # =============================================================================

    # Create a renderer and render the scene
    renderer = MatplotlibRenderer(canvas) if os.environ.get("GSP_RENDERER", "matplotlib") == "matplotlib" else DatovizRenderer(canvas)
    renderer.render([viewport], [segments], [model_matrix], [camera])
    renderer.show()


if __name__ == "__main__":
    main()
