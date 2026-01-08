"""Example demonstrating viewport NDC metric conversions."""

# pip imports
import numpy as np
from PyQt5.QtWidgets import QApplication

# local imports
from common.example_helper import ExampleHelper
from gsp.core import Canvas, Viewport
from gsp.core.camera import Camera
from gsp.visuals import Segments, Points, Texts
from gsp.types import CapStyle
from gsp_extra.bufferx import Bufferx
from gsp.types import BufferType
from gsp.types import Buffer
from gsp.constants import Constants
from gsp.utils.unit_utils import UnitUtils
from gsp.types.viewport_events_types import CanvasResizeEvent


class QtHelper:
    """Get screen properties via Qt."""

    @staticmethod
    def get_screen_ppi() -> float:
        """Get the screen pixels per inch (PPI) using Qt."""
        qt_app = QApplication([])
        screen = qt_app.primaryScreen()
        assert screen is not None, "screen MUST NOT be None"
        screen_ppi = screen.physicalDotsPerInch()
        qt_app.quit()
        return screen_ppi

    @staticmethod
    def get_device_pixel_ratio() -> float:
        """Get the screen device pixel ratio using Qt."""
        qt_app = QApplication([])
        screen = qt_app.primaryScreen()
        assert screen is not None, "screen MUST NOT be None"
        device_pixel_ratio = screen.devicePixelRatio()
        qt_app.quit()
        return device_pixel_ratio


class ViewportUnitConverter:
    """Convert between pixel/cm to ndc units in a viewport."""

    def __init__(self, canvas: Canvas, viewport: Viewport) -> None:
        """Initialize the converter with a canvas and viewport."""
        self._canvas = canvas
        self._viewport = viewport

    def _get_canvas_width_px(self) -> int:
        return self._canvas.get_width()

    def _get_canvas_height_px(self) -> int:
        return self._canvas.get_height()

    def _get_canvas_width_cm(self) -> float:
        screen_ppi = self._canvas.get_dpi()
        canvas_width_in = self._canvas.get_width() / screen_ppi
        canvas_width_cm = UnitUtils.in_to_cm(canvas_width_in)
        return canvas_width_cm

    def _get_canvas_height_cm(self) -> float:
        screen_ppi = self._canvas.get_dpi()
        canvas_height_in = self._canvas.get_height() / screen_ppi
        canvas_height_cm = UnitUtils.in_to_cm(canvas_height_in)
        return canvas_height_cm

    def _get_viewport_width_px(self) -> int:
        return self._viewport.get_width()

    def _get_viewport_height_px(self) -> int:
        return self._viewport.get_height()

    def _get_viewport_width_cm(self) -> float:
        canvas_viewport_ratio = self._viewport.get_width() / self._canvas.get_width()
        canvas_width_cm = self._get_canvas_width_cm()
        viewport_width_cm = canvas_viewport_ratio * canvas_width_cm
        return viewport_width_cm

    def _get_viewport_height_cm(self) -> float:
        canvas_viewport_ratio = self._viewport.get_height() / self._canvas.get_height()
        canvas_height_cm = self._get_canvas_height_cm()
        viewport_height_cm = canvas_viewport_ratio * canvas_height_cm
        return viewport_height_cm

    def pixel_to_ndc(self, delta_pixel_x: float, delta_pixel_y: float) -> tuple[float, float]:
        """Convert a delta in pixels to a delta in NDC units."""
        viewport_range_ndc_x = 2.0
        viewport_range_ndc_y = 2.0

        delta_ndc_x = (delta_pixel_x / self._get_viewport_width_px()) * viewport_range_ndc_x
        delta_ndc_y = (delta_pixel_y / self._get_viewport_height_px()) * viewport_range_ndc_y

        return (delta_ndc_x, delta_ndc_y)

    def cm_to_ndc(self, delta_cm_x: float, delta_cm_y: float) -> tuple[float, float]:
        """Convert a delta in cm to a delta in NDC units."""
        viewport_range_ndc_x = 2.0
        viewport_range_ndc_y = 2.0

        delta_ndc_x = (delta_cm_x / self._get_viewport_width_cm()) * viewport_range_ndc_x
        delta_ndc_y = (delta_cm_y / self._get_viewport_height_cm()) * viewport_range_ndc_y

        return (delta_ndc_x, delta_ndc_y)


def main():
    """Example demonstrating viewport NDC metric conversions."""
    # fix random seed for reproducibility
    np.random.seed(0)

    def create_canvas(canvas_width_cm: float, canvas_height_cm: float) -> Canvas:
        screen_ppi = QtHelper.get_screen_ppi()
        canvas_width_in = UnitUtils.cm_to_in(canvas_width_cm)
        canvas_height_in = UnitUtils.cm_to_in(canvas_height_cm)
        canvas_width_px = round(canvas_width_in * screen_ppi)
        canvas_height_px = round(canvas_height_in * screen_ppi)
        canvas = Canvas(width=canvas_width_px, height=canvas_height_px, dpi=screen_ppi)
        return canvas

    # Create a canvas
    canvas_width_cm = 5
    canvas_height_cm = 5
    canvas = create_canvas(canvas_width_cm, canvas_height_cm)

    # Create a viewport and add it to the canvas
    viewport = Viewport(0, 0, canvas.get_width(), canvas.get_height())

    viewport_unit = ViewportUnitConverter(canvas, viewport)
    print("Canvas width (px):", viewport_unit._get_canvas_width_px())
    print("Canvas width (cm):", viewport_unit._get_canvas_width_cm())
    print("Viewport width (px):", viewport_unit._get_viewport_width_px())
    print("Viewport width (cm):", viewport_unit._get_viewport_width_cm())

    # =============================================================================
    #
    # =============================================================================

    def generate_axes_segments(viewport_unit: ViewportUnitConverter) -> Segments:
        segments_count = 2

        positions_numpy = np.array(
            [
                [-1.0, +0.0, 0.0],
                [+1.0, +0.0, 0.0],
                [+0.0, +1.0, 0.0],
                [+0.0, -1.0, 0.0],
            ],
            dtype=np.float32,
        )
        positions_buffer = Bufferx.from_numpy(positions_numpy, BufferType.vec3)

        line_widths_numpy = np.array([UnitUtils.pixel_to_point(2, canvas.get_dpi())] * segments_count, dtype=np.float32)
        line_widths_buffer = Bufferx.from_numpy(line_widths_numpy, BufferType.float32)

        colors_buffer = Buffer(segments_count, BufferType.rgba8)
        colors_buffer.set_data(Constants.Color.black * segments_count, 0, segments_count)

        segments = Segments(positions_buffer, line_widths_buffer, CapStyle.BUTT, colors_buffer)
        return segments

    def generate_ticks_horizontal(viewport_unit: ViewportUnitConverter) -> Segments:
        viewport_width_cm = viewport_unit._get_viewport_width_cm()
        num_ticks = int(viewport_width_cm)

        delta_ndc_x, delta_ndc_y = viewport_unit.cm_to_ndc(1.0, 0.2)

        # Create positions for ticks from -num_ticks/2 to +num_ticks/2
        positions_array = []
        for tick_index in range(-num_ticks // 2, num_ticks // 2 + 1):
            if tick_index == 0:
                continue
            tick_x = delta_ndc_x * tick_index
            positions_array.append([tick_x, +0.0, 0.0])
            positions_array.append([tick_x, -delta_ndc_y, 0.0])

        positions_numpy = np.array(positions_array, dtype=np.float32)
        positions_buffer = Bufferx.from_numpy(positions_numpy, BufferType.vec3)

        # sanitity checks
        assert positions_buffer.get_count() % 2 == 0
        segments_count = positions_buffer.get_count() // 2
        assert segments_count == positions_buffer.get_count() / 2

        line_widths_numpy = np.array([UnitUtils.pixel_to_point(1, canvas.get_dpi())] * segments_count, dtype=np.float32)
        line_widths_buffer = Bufferx.from_numpy(line_widths_numpy, BufferType.float32)

        colors_buffer = Buffer(segments_count, BufferType.rgba8)
        colors_buffer.set_data(Constants.Color.black * segments_count, 0, segments_count)

        segments = Segments(positions_buffer, line_widths_buffer, CapStyle.BUTT, colors_buffer)
        return segments

    def generate_ticks_vertical(viewport_unit: ViewportUnitConverter) -> Segments:
        viewport_height_cm = viewport_unit._get_viewport_height_cm()
        num_ticks = int(viewport_height_cm)

        delta_ndc_x, delta_ndc_y = viewport_unit.cm_to_ndc(0.2, 1.0)

        # Create positions for ticks from -num_ticks/2 to +num_ticks/2
        positions_array = []
        for tick_index in range(-num_ticks // 2, num_ticks // 2 + 1):
            if tick_index == 0:
                continue
            tick_y = delta_ndc_y * tick_index
            positions_array.append([+0.0, tick_y, 0.0])
            positions_array.append([-delta_ndc_x, tick_y, 0.0])

        positions_numpy = np.array(positions_array, dtype=np.float32)
        positions_buffer = Bufferx.from_numpy(positions_numpy, BufferType.vec3)

        # sanitity checks
        assert positions_buffer.get_count() % 2 == 0
        segments_count = positions_buffer.get_count() // 2
        assert segments_count == positions_buffer.get_count() / 2

        line_widths_numpy = np.array([UnitUtils.pixel_to_point(1, canvas.get_dpi())] * segments_count, dtype=np.float32)
        line_widths_buffer = Bufferx.from_numpy(line_widths_numpy, BufferType.float32)

        colors_buffer = Buffer(segments_count, BufferType.rgba8)
        colors_buffer.set_data(Constants.Color.black * segments_count, 0, segments_count)

        segments = Segments(positions_buffer, line_widths_buffer, CapStyle.BUTT, colors_buffer)
        return segments

    def generate_axes_texts_horizontal(viewport_unit: ViewportUnitConverter) -> Texts:
        viewport_width_cm = viewport_unit._get_viewport_width_cm()
        num_ticks = int(viewport_width_cm)

        delta_ndc_x, delta_ndc_y = viewport_unit.cm_to_ndc(1.0, 0.2)

        # Create positions for ticks from -num_ticks/2 to +num_ticks/2
        positions_array = []
        for tick_index in range(-num_ticks // 2, num_ticks // 2 + 1):
            if tick_index == 0:
                continue
            tick_x = delta_ndc_x * tick_index
            positions_array.append([tick_x, -delta_ndc_y * 1.3, 0.0])

        positions_numpy = np.array(positions_array, dtype=np.float32)
        positions_buffer = Bufferx.from_numpy(positions_numpy, BufferType.vec3)

        strings = []
        for tick_index in range(-num_ticks // 2, num_ticks // 2 + 1):
            if tick_index == 0:
                continue
            strings.append(f"{tick_index}")
        string_count = len(strings)

        colors_buffer = Buffer(string_count, BufferType.rgba8)
        colors_buffer.set_data(Constants.Color.black * string_count, 0, string_count)

        font_size_numpy = np.array([UnitUtils.pixel_to_point(12, canvas.get_dpi())] * string_count, dtype=np.float32)
        font_size_buffer = Bufferx.from_numpy(font_size_numpy, BufferType.float32)

        # Create a anchor_numpy for each string with a bottom-left anchor
        anchors_numpy = np.array([[0, 1] for _ in range(string_count)], dtype=np.float32)
        anchors_buffer = Bufferx.from_numpy(anchors_numpy, BufferType.vec2)

        angles_numpy = np.array([[0] for _ in range(string_count)], dtype=np.float32)
        angles_buffer = Bufferx.from_numpy(angles_numpy, BufferType.float32)

        font_name = "Arial"

        # Create the Texts visual
        texts = Texts(positions_buffer, strings, colors_buffer, font_size_buffer, anchors_buffer, angles_buffer, font_name)

        return texts

    def generate_axes_texts_vertical(viewport_unit: ViewportUnitConverter) -> Texts:
        viewport_height_cm = viewport_unit._get_viewport_height_cm()
        num_ticks = int(viewport_height_cm)

        delta_ndc_x, delta_ndc_y = viewport_unit.cm_to_ndc(0.2, 1.0)

        # Create positions for ticks from -num_ticks/2 to +num_ticks/2
        positions_array = []
        for tick_index in range(-num_ticks // 2, num_ticks // 2 + 1):
            if tick_index == 0:
                continue
            tick_y = delta_ndc_y * tick_index
            positions_array.append([-delta_ndc_x * 1.3, tick_y, 0.0])

        positions_numpy = np.array(positions_array, dtype=np.float32)
        positions_buffer = Bufferx.from_numpy(positions_numpy, BufferType.vec3)

        strings = []
        for tick_index in range(-num_ticks // 2, num_ticks // 2 + 1):
            if tick_index == 0:
                continue
            strings.append(f"{tick_index}")
        string_count = len(strings)

        colors_buffer = Buffer(string_count, BufferType.rgba8)
        colors_buffer.set_data(Constants.Color.black * string_count, 0, string_count)

        font_size_numpy = np.array([UnitUtils.pixel_to_point(12, canvas.get_dpi())] * string_count, dtype=np.float32)
        font_size_buffer = Bufferx.from_numpy(font_size_numpy, BufferType.float32)

        # Create a anchor_numpy for each string with a bottom-left anchor
        anchors_numpy = np.array([[1, 0] for _ in range(string_count)], dtype=np.float32)
        anchors_buffer = Bufferx.from_numpy(anchors_numpy, BufferType.vec2)

        angles_numpy = np.array([[0] for _ in range(string_count)], dtype=np.float32)
        angles_buffer = Bufferx.from_numpy(angles_numpy, BufferType.float32)

        font_name = "Arial"

        # Create the Texts visual
        texts = Texts(positions_buffer, strings, colors_buffer, font_size_buffer, anchors_buffer, angles_buffer, font_name)

        return texts

    axes_segments = generate_axes_segments(viewport_unit)
    axes_ticks_horizontal = generate_ticks_horizontal(viewport_unit)
    axes_ticks_vertical = generate_ticks_vertical(viewport_unit)
    axes_texts_horizontal = generate_axes_texts_horizontal(viewport_unit)
    axes_texts_vertical = generate_axes_texts_vertical(viewport_unit)

    # =============================================================================
    #
    # =============================================================================
    def generate_points(viewport_unit: ViewportUnitConverter) -> Points:
        point_count = 1

        delta_ndc_x, delta_ndc_y = viewport_unit.cm_to_ndc(1.0, 1.0)

        point_x = delta_ndc_x
        point_y = delta_ndc_y

        # Random positions - Create buffer from numpy array
        positions_buffer = Bufferx.from_numpy(np.array([[point_x, point_y, 0.0]], dtype=np.float32), BufferType.vec3)

        # Sizes - Create buffer and set data with numpy array
        sizes_numpy = np.array([10] * point_count, dtype=np.float32)
        sizes_buffer = Bufferx.from_numpy(sizes_numpy, BufferType.float32)

        # all pixels red - Create buffer and fill it with a constant
        face_colors_buffer = Buffer(point_count, BufferType.rgba8)
        face_colors_buffer.set_data(Constants.Color.red * point_count, 0, point_count)

        # Edge colors - Create buffer and fill it with a constant
        edge_colors_buffer = Buffer(point_count, BufferType.rgba8)
        edge_colors_buffer.set_data(Constants.Color.black * point_count, 0, point_count)

        # Edge widths - Create buffer and fill it with a constant
        edge_widths_numpy = np.array([UnitUtils.pixel_to_point(0.5, canvas.get_dpi())] * point_count, dtype=np.float32)
        edge_widths_buffer = Bufferx.from_numpy(edge_widths_numpy, BufferType.float32)

        # Create the Points visual and add it to the viewport
        points = Points(positions_buffer, sizes_buffer, face_colors_buffer, edge_colors_buffer, edge_widths_buffer)
        return points

    points = generate_points(viewport_unit)

    # =============================================================================
    #
    # =============================================================================

    model_matrix = Bufferx.mat4_identity()
    camera = Camera(Bufferx.mat4_identity(), Bufferx.mat4_identity())

    renderer_name = ExampleHelper.get_renderer_name()
    renderer_base = ExampleHelper.create_renderer(renderer_name, canvas)
    renderer_base.render(
        [viewport, viewport, viewport, viewport, viewport, viewport],
        [axes_segments, axes_ticks_horizontal, axes_ticks_vertical, axes_texts_horizontal, axes_texts_vertical, points],
        [model_matrix, model_matrix, model_matrix, model_matrix, model_matrix, model_matrix],
        [camera, camera, camera, camera, camera, camera],
    )

    # =============================================================================
    #
    # =============================================================================

    # NOTE: it MUST be done as little as possible as those variables are in `int`
    # - so there is a loss of precision everytime it is computed
    viewport_canvas_ratio_x: float = viewport.get_x() / canvas.get_width()
    viewport_canvas_ratio_y: float = viewport.get_y() / canvas.get_height()
    viewport_canvas_ratio_w: float = viewport.get_width() / canvas.get_width()
    viewport_canvas_ratio_h: float = viewport.get_height() / canvas.get_height()

    def on_canvas_resize(canvas_resize_event: CanvasResizeEvent):
        nonlocal canvas, viewport
        nonlocal axes_segments
        nonlocal axes_ticks_horizontal
        nonlocal axes_ticks_vertical
        nonlocal axes_texts_horizontal
        nonlocal axes_texts_vertical
        nonlocal points

        print("canvas_resize_event", canvas_resize_event)

        # resize the canvas
        canvas.set_width(canvas_resize_event.canvas_width_px)
        canvas.set_height(canvas_resize_event.canvas_height_px)

        # set viewport size according to previous ratios
        viewport.set_x(int(canvas.get_width() * viewport_canvas_ratio_x))
        viewport.set_y(int(canvas.get_height() * viewport_canvas_ratio_y))
        viewport.set_width(int(canvas.get_width() * viewport_canvas_ratio_w))
        viewport.set_height(int(canvas.get_height() * viewport_canvas_ratio_h))

        # get current uuids
        axes_segments_uuid = axes_segments.get_uuid()
        axes_ticks_horizontal_uuid = axes_ticks_horizontal.get_uuid()
        axes_ticks_vertical_uuid = axes_ticks_vertical.get_uuid()
        axes_texts_horizontal_uuid = axes_texts_horizontal.get_uuid()
        axes_texts_vertical_uuid = axes_texts_vertical.get_uuid()
        points_uuid = points.get_uuid()

        # recreate all the visuals
        axes_segments = generate_axes_segments(viewport_unit)
        axes_ticks_horizontal = generate_ticks_horizontal(viewport_unit)
        axes_ticks_vertical = generate_ticks_vertical(viewport_unit)
        axes_texts_horizontal = generate_axes_texts_horizontal(viewport_unit)
        axes_texts_vertical = generate_axes_texts_vertical(viewport_unit)
        points = generate_points(viewport_unit)

        # restore uuids for the new visuals
        axes_segments._uuid = axes_segments_uuid
        axes_ticks_horizontal._uuid = axes_ticks_horizontal_uuid
        axes_ticks_vertical._uuid = axes_ticks_vertical_uuid
        axes_texts_horizontal._uuid = axes_texts_horizontal_uuid
        axes_texts_vertical._uuid = axes_texts_vertical_uuid
        points._uuid = points_uuid

        # rerender all the visuals
        renderer_base.render(
            [viewport, viewport, viewport, viewport, viewport, viewport],
            [axes_segments, axes_ticks_horizontal, axes_ticks_vertical, axes_texts_horizontal, axes_texts_vertical, points],
            [model_matrix, model_matrix, model_matrix, model_matrix, model_matrix, model_matrix],
            [camera, camera, camera, camera, camera, camera],
        )

    # create viewport events and subscribe to canvas resize
    viewport_events = ExampleHelper.create_viewport_events(renderer_base, viewport)
    viewport_events.canvas_resize_event.subscribe(on_canvas_resize)

    # =============================================================================
    #
    # =============================================================================
    renderer_base.show()


if __name__ == "__main__":
    main()
