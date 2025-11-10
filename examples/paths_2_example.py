# stdlib imports
import os

# pip imports
import numpy as np
import matplotlib.pyplot

# local imports
from gsp.core import Canvas, Viewport
from gsp.visuals import Paths
from gsp.types import Buffer, BufferType
from gsp.core import Camera
from gsp_matplotlib.renderer import MatplotlibRenderer
from gsp_datoviz.renderer import DatovizRenderer
from gsp_extra.bufferx import Bufferx
from gsp.utils.group_utils import GroupUtils
from gsp.constants import Constants


def main():
    # fix random seed for reproducibility
    np.random.seed(0)

    # Create a canvas
    canvas = Canvas(100, 100, 96.0)

    # Create a viewport and add it to the canvas
    viewport = Viewport(0, 0, canvas.get_width(), canvas.get_height())

    # =============================================================================
    # Add random points
    # - various ways to create Buffers
    # =============================================================================

    # Generate multiple polylines (for example, 3 sine waves with offsets)
    num_lines = 10
    num_points = 100

    lines = []
    colors = []
    widths = []

    for i in range(num_lines):
        x = np.linspace(0, 10, num_points)
        y = np.sin(x + i) + i * 1.5  # vertical offset for each line

        # Make color vary along the line (map y to color)
        color_values = matplotlib.pyplot.cm.plasma((y - y.min()) / (y.max() - y.min()))

        # Vary linewidth by slope magnitude
        line_widths = 1 + 3.0 * np.abs(np.gradient(y))

        # Build line segments for this line
        points = np.array([x, y]).T.reshape(-1, 1, 2)
        segments = np.concatenate([points[:-1], points[1:]], axis=1)

        lines.append(segments)
        colors.append(color_values[:-1])
        widths.append(line_widths[:-1])

    # =============================================================================
    #
    # =============================================================================

    point_count = sum(len(line) for line in lines)

    # Random positions - Create buffer from numpy array
    positions_numpy = np.random.rand(point_count, 3).astype(np.float32) * 2.0 - 1
    positions_buffer = Bufferx.from_numpy(positions_numpy, BufferType.vec3)

    path_sizes_numpy = np.array([len(line) for line in lines], dtype=np.uint32)
    path_sizes_buffer = Bufferx.from_numpy(path_sizes_numpy, BufferType.uint32)

    # all pixels red - Create buffer and fill it with a constant
    colors_buffer = Buffer(point_count, BufferType.rgba8)
    colors_buffer.set_data(Constants.red * point_count, 0, point_count)

    line_widths_numpy = np.array([10.0 for _ in range(point_count)], dtype=np.float32)
    line_widths_buffer = Bufferx.from_numpy(line_widths_numpy, BufferType.float32)

    # Create the Pixels visual and add it to the viewport
    paths = Paths(positions_buffer, path_sizes_buffer, colors_buffer, line_widths_buffer)
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
    renderer.render([viewport], [paths], [model_matrix], [camera])
    renderer.show()


if __name__ == "__main__":
    main()
