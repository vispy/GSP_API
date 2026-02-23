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
from vispy_2 import scatter


def main():
    """Main function for the scatter example."""
    # fix random seed for reproducibility
    np.random.seed(0)

    # Create a canvas
    canvas = Canvas(400, 400, 72.0)

    half_width = int(canvas.get_width() / 2)
    half_height = int(canvas.get_height() / 2)

    # Create viewports
    viewport_1 = Viewport(0, 0, half_width, half_height)
    viewport_2 = Viewport(half_width, 0, half_width, half_height)
    viewport_3 = Viewport(0, half_height, half_width, half_height)
    viewport_4 = Viewport(half_width, half_height, half_width, half_height)

    # =============================================================================
    # Add random points
    # - various ways to create Buffers
    # =============================================================================

    def createVisualPixelByScatter() -> VisualBase:
        point_count = 2_000
        group_size = point_count
        group_count = GroupUtils.get_group_count(point_count, groups=group_size)

        # Random positions - Create buffer from numpy array
        positions_numpy = np.random.rand(point_count, 3).astype(np.float32) * 2.0 - 1
        positions_buffer = Bufferx.from_numpy(positions_numpy, BufferType.vec3)

        # all pixels red - Create buffer and fill it with a constant
        colors_buffer = Buffer(group_count, BufferType.rgba8)
        colors_buffer.set_data(bytearray([255, 0, 0, 255]) * group_count, 0, group_count)

        # Create the Pixels visual and add it to the viewport
        visualPixel = scatter(positions_buffer, colors=colors_buffer, groups=group_size)
        return visualPixel

    def createVisualPointsByScatter() -> VisualBase:
        point_count = 100

        # Create Buffers
        positions_numpy = np.random.uniform(-1, 1, (point_count, 3)).astype(np.float32)
        positions_numpy[:, 2] = 0.0
        positions_buffer = Bufferx.from_numpy(positions_numpy, BufferType.vec3)

        sizes_numpy = np.linspace(20, 1000, point_count).astype(np.float32)
        sizes_buffer = Bufferx.from_numpy(sizes_numpy, BufferType.float32)

        face_colors_cursor = np.linspace(0, 1, point_count).astype(np.float32)
        face_colors_buffer = CmapUtils.get_color_map("viridis", face_colors_cursor)

        edge_colors_buffer = Buffer(point_count, BufferType.rgba8)
        edge_colors_buffer.set_data(Constants.Color.white * point_count, 0, point_count)

        edge_widths_numpy = np.full(point_count, 1.0).astype(np.float32)
        edge_widths_buffer = Bufferx.from_numpy(edge_widths_numpy, BufferType.float32)

        # Create the Points visual and add it to the viewport
        visualPoints = scatter(
            positions_buffer,
            sizes=sizes_buffer,
            face_colors=face_colors_buffer,
            edge_colors=edge_colors_buffer,
            edge_widths=edge_widths_buffer,
        )
        return visualPoints

    def createVisualMarkersByScatter(marker_shape: MarkerShape) -> VisualBase:
        marker_count = 100

        # Create Buffers
        positions_numpy = np.random.uniform(-1, 1, (marker_count, 3)).astype(np.float32)
        positions_numpy[:, 2] = 0.0
        positions_buffer = Bufferx.from_numpy(positions_numpy, BufferType.vec3)

        sizes_numpy = np.linspace(20, 1000, marker_count).astype(np.float32)
        sizes_buffer = Bufferx.from_numpy(sizes_numpy, BufferType.float32)

        face_colors_cursor = np.linspace(0, 1, marker_count).astype(np.float32)
        face_colors_buffer = CmapUtils.get_color_map("plasma", face_colors_cursor)

        edge_colors_buffer = Buffer(marker_count, BufferType.rgba8)
        edge_colors_buffer.set_data(Constants.Color.black * marker_count, 0, marker_count)

        edge_widths_numpy = np.full(marker_count, 1.0).astype(np.float32)
        edge_widths_buffer = Bufferx.from_numpy(edge_widths_numpy, BufferType.float32)

        # Create the Markers visual and add it to the viewport
        visualMarkers = scatter(
            positions_buffer,
            sizes=sizes_buffer,
            face_colors=face_colors_buffer,
            edge_colors=edge_colors_buffer,
            edge_widths=edge_widths_buffer,
            marker_shape=marker_shape,
        )
        return visualMarkers

    visualPixel = createVisualPixelByScatter()
    visualPoints = createVisualPointsByScatter()
    visualMarkers1 = createVisualMarkersByScatter(MarkerShape.club)
    visualMarkers2 = createVisualMarkersByScatter(MarkerShape.square)

    # declare array of render items
    render_items: list[RenderItem] = []
    render_items.append(RenderItem(viewport_1, visualPixel, Bufferx.mat4_identity(), Camera(Bufferx.mat4_identity(), Bufferx.mat4_identity())))
    render_items.append(RenderItem(viewport_2, visualPoints, Bufferx.mat4_identity(), Camera(Bufferx.mat4_identity(), Bufferx.mat4_identity())))
    render_items.append(RenderItem(viewport_3, visualMarkers1, Bufferx.mat4_identity(), Camera(Bufferx.mat4_identity(), Bufferx.mat4_identity())))
    render_items.append(RenderItem(viewport_4, visualMarkers2, Bufferx.mat4_identity(), Camera(Bufferx.mat4_identity(), Bufferx.mat4_identity())))

    # =============================================================================
    # Render
    # =============================================================================

    # Create renderer and render
    renderer_name = ExampleHelper.get_renderer_name()
    renderer_base = ExampleHelper.create_renderer(renderer_name, canvas)

    # Render all render items
    rendered_image = renderer_base.render(
        [render_item.viewport for render_item in render_items],
        [render_item.visual_base for render_item in render_items],
        [render_item.model_matrix for render_item in render_items],
        [render_item.camera for render_item in render_items],
    )

    # Save to file
    ExampleHelper.save_output_image(rendered_image, f"{pathlib.Path(__file__).stem}_{renderer_name}.png")

    # Show the renderer
    renderer_base.show()


if __name__ == "__main__":
    main()
