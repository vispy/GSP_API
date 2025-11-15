# stdlib imports
import os
from typing import Literal

# pip imports
import numpy as np
import matplotlib.pyplot

# local imports
from gsp.core import Canvas, Viewport, VisualBase
from gsp.visuals import Pixels
from gsp.types import Buffer, BufferType
from gsp.core import Camera
from gsp_matplotlib.renderer import MatplotlibRenderer
from gsp_datoviz.renderer import DatovizRenderer
from gsp_extra.bufferx import Bufferx
from gsp.utils.group_utils import GroupUtils

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
        canvas = Canvas(100, 100, 96.0)
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
    def create_random_pixels(point_count: int, group_size: int) -> Pixels:
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
        canvas: Canvas,
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
    viewport = viewports[0]

    # =============================================================================
    # Add random points
    # - various ways to create Buffers
    # =============================================================================

    point_count = 10_000
    visuals: list[VisualBase] = []
    pixels = BigTesterVisuals.create_random_pixels(point_count, group_size=point_count)
    visuals.append(pixels)

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
