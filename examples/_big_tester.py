# stdlib imports
import os
import re
from typing import Literal, Sequence
import typing

# pip imports
import numpy as np
import argparse

# local imports
from gsp.types.renderer_base import RendererBase
from gsp.types.transbuf import TransBuf
from gsp.core import Canvas, Viewport, VisualBase
from gsp.visuals import Segments, Points, Pixels
from gsp.types import Buffer, BufferType
from gsp.core import Camera
from gsp_matplotlib.renderer import MatplotlibRenderer
from gsp_datoviz.renderer import DatovizRenderer
from gsp_network.renderer import NetworkRenderer
from gsp_extra.bufferx import Bufferx
from gsp.utils.group_utils import GroupUtils
from gsp.utils.unit_utils import UnitUtils
from gsp.constants import Constants
from gsp.types import CapStyle
from gsp.utils.cmap_utils import CmapUtils
from gsp_pydantic.serializer.pydantic_parser import PydanticParser
from gsp_pydantic.serializer.pydantic_serializer import PydanticSerializer
from gsp_pydantic.types.pydantic_dict import PydanticDict

# =============================================================================
#
# =============================================================================


class BigTesterBoilerplate:
    @staticmethod
    def init_random_seed(seed: int = 0) -> None:
        np.random.seed(seed)


class BigTesterCanvas:
    @staticmethod
    def create_canvas(viewport_count: int = 2, width: int = 100, dpi: float = 96.0) -> Canvas:
        scale = 3
        size = width * viewport_count
        scaled_width = int(size * scale)
        scaled_height = int(width * scale)
        scaled_dpi = dpi * scale
        canvas = Canvas(scaled_width, scaled_height, scaled_dpi)
        return canvas


class BigTesterViewport:
    @staticmethod
    def create_viewports(canvas: Canvas, count: int) -> list[Viewport]:
        viewports: list[Viewport] = []
        viewport_width = canvas.get_width() // count
        for viewport_hori_index in range(count):
            viewport = Viewport(viewport_hori_index * viewport_width, 0, viewport_width, viewport_width)
            viewports.append(viewport)
        return viewports


class BigTesterVisuals:
    @staticmethod
    def create_random_pixels(dpi: float = 96.0) -> VisualBase:
        point_count = 10_000
        group_size = point_count  # one group per point
        group_count = GroupUtils.get_group_count(point_count, groups=group_size)

        # Random positions - Create buffer from numpy array
        positions_numpy = np.random.rand(point_count, 3).astype(np.float32) * 2.0 - 1
        positions_buffer = Bufferx.from_numpy(positions_numpy, BufferType.vec3)

        # all pixels red - Create buffer and fill it with a constant
        colors_buffer = Buffer(group_count, BufferType.rgba8)
        colors_buffer.set_data(Constants.Color.black * group_count, 0, group_count)

        # Create the Pixels visual and add it to the viewport
        pixels = Pixels(positions_buffer, colors_buffer, groups=group_size)
        return pixels

    @staticmethod
    def create_random_points(dpi: float = 96.0) -> VisualBase:
        point_count = 20

        # Random positions - Create buffer from numpy array
        positions_numpy = np.random.rand(point_count, 3).astype(np.float32) * 2.0 - 1
        positions_buffer = Bufferx.from_numpy(positions_numpy, BufferType.vec3)

        # Sizes - Create buffer and set data with numpy array
        sizes_numpy = np.array([5] * point_count, dtype=np.float32)
        sizes_buffer = Bufferx.from_numpy(sizes_numpy, BufferType.float32)

        # all pixels red - Create buffer and fill it with a constant
        face_colors_buffer = Buffer(point_count, BufferType.rgba8)
        face_colors_buffer.set_data(Constants.Color.green * point_count, 0, point_count)

        # Edge colors - Create buffer and fill it with a constant
        edge_colors_buffer = Buffer(point_count, BufferType.rgba8)
        edge_colors_buffer.set_data(Constants.Color.blue * point_count, 0, point_count)

        # Edge widths - Create buffer and fill it with a constant
        edge_widths_numpy = np.array([UnitUtils.pixel_to_point(1, dpi)] * point_count, dtype=np.float32)
        edge_widths_buffer = Bufferx.from_numpy(edge_widths_numpy, BufferType.float32)

        # Create the Points visual and add it to the viewport
        points = Points(positions_buffer, sizes_buffer, face_colors_buffer, edge_colors_buffer, edge_widths_buffer)
        return points

    @staticmethod
    def create_spiral_pixels() -> VisualBase:
        def generate_pixels(gsp_color: bytearray) -> Pixels:
            point_count = 1_000
            group_size = point_count
            group_count = GroupUtils.get_group_count(point_count, groups=group_size)

            # Random positions - Create buffer from numpy array
            positions_angle = np.linspace(0, 4 * np.pi, point_count)
            positions_radius = np.linspace(0.0, 1.0, point_count)
            positions_x = positions_radius * np.sin(positions_angle)
            positions_y = positions_radius * np.cos(positions_angle)
            positions_z = np.zeros(point_count)
            positions_numpy = np.vstack((positions_x, positions_y, positions_z)).T.astype(np.float32)
            positions_buffer = Bufferx.from_numpy(positions_numpy, BufferType.vec3)

            # all pixels red - Create buffer and fill it with a constant
            colors_buffer = Buffer(group_count, BufferType.rgba8)
            colors_buffer.set_data(gsp_color * group_count, 0, group_count)

            # Create the Pixels visual and add it to the viewport
            pixels = Pixels(positions_buffer, colors_buffer, groups=group_size)
            return pixels

        pixels = generate_pixels(gsp_color=Constants.Color.red)
        return pixels

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

        positions_buffer, colors_buffer, line_widths_buffer = generate_data(line_count=10, line_width_max=8.0, color_map_name="plasma")

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
    def create_renderer(canvas: Canvas, renderer_name: Literal["matplotlib", "datoviz", "network"]) -> RendererBase:
        if renderer_name == "matplotlib":
            renderer = MatplotlibRenderer(canvas)
            return renderer
        elif renderer_name == "datoviz":
            renderer = DatovizRenderer(canvas)
            return renderer
        elif renderer_name == "network":

            server_base_url = "http://localhost:5000"
            renderer = NetworkRenderer(canvas, server_base_url, renderer_name="datoviz")
            return renderer
        else:
            raise ValueError(f"Unknown renderer name: {renderer_name}")

    @staticmethod
    def render_scene(
        renderer: RendererBase,
        viewports: list[Viewport],
        visuals: list[VisualBase],
        model_matrices: list[TransBuf],
        cameras: list[Camera],
    ) -> bytes:
        rendered_image = renderer.render(viewports, visuals, model_matrices, cameras)
        return rendered_image


class BigTesterSerializer:
    @staticmethod
    def serialize_visual(
        canvas: Canvas,
        viewports: list[Viewport],
        visuals: list[VisualBase],
        model_matrices: list[TransBuf],
        cameras: list[Camera],
    ) -> PydanticDict:
        # Serialize the scene
        pydantic_serializer = PydanticSerializer(canvas)
        pydantic_serial: PydanticDict = pydantic_serializer.serialize(viewports=viewports, visuals=visuals, model_matrices=model_matrices, cameras=cameras)
        return pydantic_serial

    @staticmethod
    def deserialize_visual(
        pydantic_serial: PydanticDict,
    ) -> tuple[
        Canvas,
        list[Viewport],
        list[VisualBase],
        list[TransBuf],
        list[Camera],
    ]:
        parsed_canvas, parsed_viewports, parsed_visuals, parsed_model_matrices, parsed_cameras = PydanticParser().parse(pydantic_serial)
        return parsed_canvas, parsed_viewports, parsed_visuals, parsed_model_matrices, parsed_cameras

    @staticmethod
    def serialize_cycle(
        canvas: Canvas,
        viewports: list[Viewport],
        visuals: list[VisualBase],
        model_matrices: list[TransBuf],
        cameras: list[Camera],
    ) -> tuple[
        Canvas,
        list[Viewport],
        list[VisualBase],
        list[TransBuf],
        list[Camera],
    ]:
        pydantic_serial: PydanticDict = BigTesterSerializer.serialize_visual(
            canvas,
            viewports,
            visuals,
            model_matrices,
            cameras,
        )

        parsed_canvas, parsed_viewports, parsed_visuals, parsed_model_matrices, parsed_cameras = BigTesterSerializer.deserialize_visual(
            pydantic_serial,
        )

        return parsed_canvas, parsed_viewports, parsed_visuals, parsed_model_matrices, parsed_cameras


# =============================================================================
#
# =============================================================================


def main():
    # Parse command line arguments
    argParser = argparse.ArgumentParser(
        description="Run the big tester example.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    argParser.add_argument("--viewport-count", type=int, default=1, help="Number of viewports to create")
    argParser.add_argument("--renderer-name", type=str, choices=["matplotlib", "datoviz", "network"], default="matplotlib", help="Renderer to use")
    argParser.add_argument(
        "--matplotlib-image-format", type=str, choices=["png", "svg", "pdf"], default="png", help="Matplotlib image format. Only used if renderer is matplotlib"
    )
    argParser.add_argument("--image-path", type=str, default=None, help="Path to save image")
    argParser.add_argument(
        "--pydantic-serialize-cycle",
        action="store_true",
        help="Perform a serialization cycle using Pydantic",
    )
    argParser.add_argument(
        "--scene",
        dest="scenes",
        type=str,
        default=[],
        nargs="+",
        choices=[
            "random_points",
            "random_pixels",
            "random_segments",
            "spiral_pixels",
        ],
        help="A required list of one or more scene.",
    )
    args = argParser.parse_args()

    # type casting for all command line args
    args.viewport_count = typing.cast(int, args.viewport_count)
    args.renderer_name = typing.cast(Literal["matplotlib", "datoviz", "network"], args.renderer_name)
    args.matplotlib_image_format = typing.cast(Literal["png", "svg", "pdf"], args.matplotlib_image_format)
    args.image_path = typing.cast(str | None, args.image_path)
    args.pydantic_serialize_cycle = typing.cast(bool, args.pydantic_serialize_cycle)
    args.scenes = typing.cast(Sequence[str], args.scenes)

    # fix random seed for reproducibility
    BigTesterBoilerplate.init_random_seed(0)

    # Create a canvas
    canvas = BigTesterCanvas.create_canvas(args.viewport_count)

    # Create a viewport and add it to the canvas
    viewports = BigTesterViewport.create_viewports(canvas, args.viewport_count)

    # =============================================================================
    # Add random points
    # - various ways to create Buffers
    # =============================================================================

    visuals: list[VisualBase] = []
    if "random_points" in args.scenes:
        visuals.append(BigTesterVisuals.create_random_pixels(dpi=canvas.get_dpi()))
    if "random_pixels" in args.scenes:
        visuals.append(BigTesterVisuals.create_random_points(dpi=canvas.get_dpi()))
    if "random_segments" in args.scenes:
        visuals.append(BigTesterVisuals.create_random_segments())
    if "spiral_pixels" in args.scenes:
        visuals.append(BigTesterVisuals.create_spiral_pixels())

    # =============================================================================
    # Render the canvas
    # =============================================================================

    model_matrix = BigTesterCamera.create_model_matrix()
    camera = BigTesterCamera.create_camera()

    # =============================================================================
    # Render
    # =============================================================================

    full_visuals: list[VisualBase] = visuals * len(viewports)
    full_viewports: list[Viewport] = viewports * len(visuals)
    model_matrices: list[TransBuf] = [model_matrix] * len(full_visuals)
    cameras: list[Camera] = [camera] * len(full_visuals)

    # =============================================================================
    # Serialisation cycle
    # =============================================================================

    if args.pydantic_serialize_cycle:
        canvas, viewports, visuals, model_matrices, cameras = BigTesterSerializer.serialize_cycle(
            canvas,
            full_viewports,
            full_visuals,
            model_matrices,
            cameras,
        )

    # =============================================================================
    # Render and display on screen
    # =============================================================================

    # --renderer_name matplotlib|datoviz|network

    # Create a renderer and render the scene
    renderer = BigTesterRenderer.create_renderer(canvas, renderer_name=args.renderer_name)
    rendered_image = BigTesterRenderer.render_scene(renderer, full_viewports, full_visuals, model_matrices, cameras)

    if args.image_path is not None:
        with open(args.image_path, "wb") as image_file:
            image_file.write(rendered_image)
        print(f"Rendered image saved to: {args.image_path}")

    if args.renderer_name == "matplotlib" or args.renderer_name == "datoviz":
        typed_renderer = typing.cast(MatplotlibRenderer | DatovizRenderer, renderer)
        typed_renderer.show()


if __name__ == "__main__":
    main()
