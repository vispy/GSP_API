# stdlib imports
import os

# pip imports
import numpy as np

# local imports
from gsp.core import Canvas, Viewport
from gsp.visuals import Markers
from gsp.types import Buffer, BufferType, CapStyle, JoinStyle, MarkerShape
from gsp.core import Camera
from gsp_matplotlib.renderer import MatplotlibRenderer
from gsp_datoviz.renderer import DatovizRenderer
from gsp_extra.bufferx import Bufferx
from gsp.utils.cmap_utils import CmapUtils
from gsp.constants import Constants


def main():
    # fix random seed for reproducibility
    np.random.seed(0)

    # Create a canvas
    canvas = Canvas(512, 512, 96.0)

    # Create a viewport and add it to the canvas
    viewport = Viewport(0, 0, canvas.get_width(), canvas.get_height())

    # =============================================================================
    #
    # =============================================================================

    marker_count = 100

    # Create Buffers
    positions_numpy = np.random.uniform(-1, 1, (marker_count, 3)).astype(np.float32)
    positions_numpy[:, 2] = 0.0
    positions_buffer = Bufferx.from_numpy(positions_numpy, BufferType.vec3)

    sizes_numpy = np.linspace(20, 200, marker_count).astype(np.float32)
    sizes_buffer = Bufferx.from_numpy(sizes_numpy, BufferType.float32)

    face_colors_cursor = np.linspace(0, 1, marker_count).astype(np.float32)
    face_colors_buffer = CmapUtils.get_color_map("viridis", face_colors_cursor)

    edge_colors_buffer = Buffer(marker_count, BufferType.rgba8)
    edge_colors_buffer.set_data(Constants.Colors.black * marker_count, 0, marker_count)

    edge_widths_numpy = np.full(marker_count, 1.0).astype(np.float32)
    edge_widths_buffer = Bufferx.from_numpy(edge_widths_numpy, BufferType.float32)

    # Create the Pixels visual and add it to the viewport
    markers = Markers(MarkerShape.club, positions_buffer, sizes_buffer, face_colors_buffer, edge_colors_buffer, edge_widths_buffer)
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
    renderer.render([viewport], [markers], [model_matrix], [camera])
    renderer.show()


if __name__ == "__main__":
    main()
