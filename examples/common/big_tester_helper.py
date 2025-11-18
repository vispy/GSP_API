# stdlib imports
from typing import Literal
import typing

# pip imports
import numpy as np

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
    def create_random_pixels(dpi: float = 96.0) -> tuple[VisualBase, TransBuf, Camera]:
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

        # model matrix and camera
        model_matrix = Bufferx.mat4_identity()
        camera = Camera(Bufferx.mat4_identity(), Bufferx.mat4_identity())

        # return everything
        return pixels, model_matrix, camera

    @staticmethod
    def create_random_points(dpi: float = 96.0) -> tuple[VisualBase, TransBuf, Camera]:
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

        # model matrix and camera
        model_matrix = Bufferx.mat4_identity()
        camera = Camera(Bufferx.mat4_identity(), Bufferx.mat4_identity())

        # return everything
        return points, model_matrix, camera

    @staticmethod
    def create_spiral_pixels() -> tuple[VisualBase, TransBuf, Camera]:
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

        # model matrix and camera
        model_matrix = Bufferx.mat4_identity()
        camera = Camera(Bufferx.mat4_identity(), Bufferx.mat4_identity())

        # return everything
        return pixels, model_matrix, camera

    @staticmethod
    def create_random_segments() -> tuple[VisualBase, TransBuf, Camera]:
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

        # model matrix and camera
        model_matrix = Bufferx.mat4_identity()
        camera = Camera(Bufferx.mat4_identity(), Bufferx.mat4_identity())

        # return everything
        return segments, model_matrix, camera


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
# class BigTesterRunner
# =============================================================================
class BigTesterRunner:

    @staticmethod
    def run(
        viewport_count: int,
        renderer_name: Literal["matplotlib", "datoviz", "network"],
        matplotlib_image_format: Literal["png", "svg", "pdf"],
        image_path: str | None,
        pydantic_serialize_cycle: bool,
        scenes: Literal["random_points", "random_pixels", "random_segments", "spiral_pixels"],
    ) -> None:
        # fix random seed for reproducibility
        BigTesterBoilerplate.init_random_seed(0)

        # Create a canvas
        canvas = BigTesterCanvas.create_canvas(viewport_count)

        # Create a viewport and add it to the canvas
        viewports = BigTesterViewport.create_viewports(canvas, viewport_count)

        # =============================================================================
        # Add random points
        # - various ways to create Buffers
        # =============================================================================

        visuals: list[VisualBase] = []
        model_matrices: list[TransBuf] = []
        cameras: list[Camera] = []

        if "random_pixels" in scenes:
            pixels, model_matrix, camera = BigTesterVisuals.create_random_pixels(dpi=canvas.get_dpi())
            visuals.append(pixels)
            model_matrices.append(model_matrix)
            cameras.append(camera)
        if "random_points" in scenes:
            points, model_matrix, camera = BigTesterVisuals.create_random_points(dpi=canvas.get_dpi())
            visuals.append(points)
            model_matrices.append(model_matrix)
            cameras.append(camera)
        if "random_segments" in scenes:
            segments, model_matrix, camera = BigTesterVisuals.create_random_segments()
            visuals.append(segments)
            model_matrices.append(model_matrix)
            cameras.append(camera)
        if "spiral_pixels" in scenes:
            spiral_pixels, model_matrix, camera = BigTesterVisuals.create_spiral_pixels()
            visuals.append(spiral_pixels)
            model_matrices.append(model_matrix)
            cameras.append(camera)

        # =============================================================================
        # Render the canvas
        # =============================================================================

        model_matrix = BigTesterCamera.create_model_matrix()
        camera = BigTesterCamera.create_camera()

        # =============================================================================
        # Render
        # =============================================================================

        full_visuals: list[VisualBase] = visuals * len(viewports)
        full_model_matrices: list[TransBuf] = model_matrices * len(viewports)
        full_cameras: list[Camera] = cameras * len(viewports)
        full_viewports: list[Viewport] = viewports * len(visuals)

        # =============================================================================
        # Serialisation cycle
        # =============================================================================

        if pydantic_serialize_cycle:
            canvas, viewports, visuals, model_matrices, cameras = BigTesterSerializer.serialize_cycle(
                canvas,
                full_viewports,
                full_visuals,
                full_model_matrices,
                full_cameras,
            )

        # =============================================================================
        # Render and display on screen
        # =============================================================================

        # Create a renderer and render the scene
        renderer = BigTesterRenderer.create_renderer(canvas, renderer_name=renderer_name)
        rendered_image = BigTesterRenderer.render_scene(renderer, full_viewports, full_visuals, full_model_matrices, full_cameras)

        # Save the rendered image to a file
        if image_path is not None:
            with open(image_path, "wb") as image_file:
                image_file.write(rendered_image)
            print(f"Rendered image saved to: {image_path}")

        # Show the rendered image on screen
        if renderer_name == "matplotlib" or renderer_name == "datoviz":
            typed_renderer = typing.cast(MatplotlibRenderer | DatovizRenderer, renderer)
            typed_renderer.show()
