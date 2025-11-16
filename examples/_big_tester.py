# stdlib imports
import os
from typing import Literal

# pip imports
import numpy as np
import matplotlib.pyplot

# local imports
from gsp.core import Canvas, Viewport, VisualBase
from gsp.visuals import Segments, Points, Pixels
from gsp.types import Buffer, BufferType
from gsp.core import Camera
from gsp_matplotlib.renderer import MatplotlibRenderer
from gsp_datoviz.renderer import DatovizRenderer
from gsp_extra.bufferx import Bufferx
from gsp.utils.group_utils import GroupUtils
from gsp.utils.unit_utils import UnitUtils
from gsp.constants import Constants
from gsp.types import CapStyle
from gsp.utils.cmap_utils import CmapUtils

# =============================================================================
#
# =============================================================================


class BigTesterBoilerplate:
    @staticmethod
    def init_random_seed(seed: int = 0) -> None:
        np.random.seed(seed)


class BigTesterCanvas:
    @staticmethod
    def create_canvas() -> Canvas:
        canvas = Canvas(512, 512, 96.0)
        return canvas


class BigTesterViewport:
    @staticmethod
    def create_viewports(canvas: Canvas, horizontal_count: int, vertical_count: int) -> list[Viewport]:
        viewports: list[Viewport] = []
        viewport_width = canvas.get_width() // horizontal_count
        viewport_height = canvas.get_height() // vertical_count
        for viewport_hori_index in range(horizontal_count):
            for viewport_vert_index in range(vertical_count):
                viewport = Viewport(viewport_hori_index * viewport_width, viewport_vert_index * viewport_height, viewport_width, viewport_height)
                viewports.append(viewport)
        return viewports


class BigTesterVisuals:
    @staticmethod
    def create_random_pixels(dpi: float = 96.0) -> VisualBase:
        point_count = 1_000
        group_size = point_count  # one group per point
        group_count = GroupUtils.get_group_count(point_count, groups=group_size)

        # Random positions - Create buffer from numpy array
        positions_numpy = np.random.rand(point_count, 3).astype(np.float32) * 2.0 - 1
        positions_buffer = Bufferx.from_numpy(positions_numpy, BufferType.vec3)

        # all pixels red - Create buffer and fill it with a constant
        colors_buffer = Buffer(group_count, BufferType.rgba8)
        colors_buffer.set_data(bytearray([255, 0, 0, 255]) * group_count, 0, group_count)

        # Create the Pixels visual and add it to the viewport
        pixels = Pixels(positions_buffer, colors_buffer, groups=group_size)
        return pixels

    @staticmethod
    def create_random_points(dpi: float = 96.0) -> VisualBase:
        point_count = 1_000
        group_size = point_count
        group_count = GroupUtils.get_group_count(point_count, groups=group_size)

        # Random positions - Create buffer from numpy array
        positions_numpy = np.random.rand(point_count, 3).astype(np.float32) * 2.0 - 1
        positions_buffer = Bufferx.from_numpy(positions_numpy, BufferType.vec3)

        # Sizes - Create buffer and set data with numpy array
        sizes_numpy = np.array([40] * group_count, dtype=np.float32)
        sizes_buffer = Bufferx.from_numpy(sizes_numpy, BufferType.float32)

        # all pixels red - Create buffer and fill it with a constant
        face_colors_buffer = Buffer(group_count, BufferType.rgba8)
        face_colors_buffer.set_data(bytearray([255, 0, 0, 255]) * group_count, 0, group_count)

        # Edge colors - Create buffer and fill it with a constant
        edge_colors_buffer = Buffer(group_count, BufferType.rgba8)
        edge_colors_buffer.set_data(Constants.Color.blue * group_count, 0, group_count)

        # Edge widths - Create buffer and fill it with a constant
        edge_widths_numpy = np.array([UnitUtils.pixel_to_point(1, dpi)] * group_count, dtype=np.float32)
        edge_widths_buffer = Bufferx.from_numpy(edge_widths_numpy, BufferType.float32)

        # Create the Points visual and add it to the viewport
        points = Points(positions_buffer, sizes_buffer, face_colors_buffer, edge_colors_buffer, edge_widths_buffer, groups=group_size)
        return points

    @staticmethod
    def create_random_segments() -> VisualBase:
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
        return segments


class BigTesterCamera:
    @staticmethod
    def create_camera() -> Camera:
        return Camera(Bufferx.mat4_identity(), Bufferx.mat4_identity())

    @staticmethod
    def create_model_matrix() -> Buffer:
        return Bufferx.mat4_identity()


class BigTesterRenderer:
    @staticmethod
    def create_renderer(canvas: Canvas, renderer_name: Literal["matplotlib", "datoviz"] | None = None) -> MatplotlibRenderer | DatovizRenderer:
        renderer_name = renderer_name if renderer_name is not None else "matplotlib"
        if renderer_name == "matplotlib":
            renderer = MatplotlibRenderer(canvas)
            return renderer
        elif renderer_name == "datoviz":
            renderer = DatovizRenderer(canvas)
            return renderer
        else:
            raise ValueError(f"Unknown renderer name: {renderer_name}")

    @staticmethod
    def render_scene(
        canvas: Canvas | None = None,
        renderer: MatplotlibRenderer | DatovizRenderer | None = None,
        viewports: list[Viewport] | None = None,
        visuals: list[VisualBase] | None = None,
        model_matrices: list[Buffer] | None = None,
        cameras: list[Camera] | None = None,
    ) -> None:
        canvas = canvas if canvas is not None else BigTesterCanvas.create_canvas()
        renderer = renderer if renderer is not None else BigTesterRenderer.create_renderer(canvas, renderer_name="matplotlib")
        viewports = viewports if viewports is not None else BigTesterViewport.create_viewports(canvas, 1, 1)
        visuals = visuals if visuals is not None else []
        model_matrices = model_matrices if model_matrices is not None else [BigTesterCamera.create_model_matrix()] * len(visuals)
        cameras = cameras if cameras is not None else [BigTesterCamera.create_camera()] * len(visuals)

        renderer.render(viewports, visuals, model_matrices, cameras)
        renderer.show()


# =============================================================================
#
# =============================================================================


def main():
    # fix random seed for reproducibility
    BigTesterBoilerplate.init_random_seed(0)

    # Create a canvas
    canvas = BigTesterCanvas.create_canvas()

    # Create a viewport and add it to the canvas
    viewports = BigTesterViewport.create_viewports(canvas, 1, 1)

    # =============================================================================
    # Add random points
    # - various ways to create Buffers
    # =============================================================================

    visuals: list[VisualBase] = []

    point_count = 10_000
    # visuals.append(BigTesterVisuals.create_random_pixels(dpi=canvas.get_dpi()))
    # visuals.append(BigTesterVisuals.create_random_points(dpi=canvas.get_dpi()))
    visuals.append(BigTesterVisuals.create_random_segments())

    # =============================================================================
    # Render the canvas
    # =============================================================================

    model_matrix = BigTesterCamera.create_model_matrix()
    camera = BigTesterCamera.create_camera()

    # =============================================================================
    # Render
    # =============================================================================

    # Create a renderer and render the scene
    renderer = BigTesterRenderer.create_renderer(canvas, renderer_name="matplotlib")
    BigTesterRenderer.render_scene(canvas, renderer, viewports, visuals, [model_matrix], [camera])


if __name__ == "__main__":
    main()
