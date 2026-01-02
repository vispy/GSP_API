"""Example demonstrating viewport NDC metric conversions."""

# stdlib imports
import math

# pip imports
import numpy as np
from PyQt5.QtWidgets import QApplication
from dataclasses import dataclass
import colorama

# local imports
from common.example_helper import ExampleHelper
from gsp.core import Canvas, Viewport
from gsp.core.camera import Camera
from gsp.visuals import Segments, Points, Texts
from gsp.types.visual_base import VisualBase
from gsp.types import CapStyle
from gsp_extra.bufferx import Bufferx
from gsp.types import BufferType
from gsp.types import Buffer
from gsp.constants import Constants
from gsp.utils.unit_utils import UnitUtils
from gsp_extra.viewport_events.viewport_events_types import CanvasResizeEvent
from gsp_extra.mpl3d import glm
from gsp_extra.viewport_events.viewport_events_types import CanvasResizeEvent, KeyEvent, MouseEvent
from gsp_extra.viewport_events.viewport_events_base import ViewportEventsBase


# =============================================================================
# Colorama alias
# =============================================================================
def text_cyan(text: str) -> str:
    return colorama.Fore.CYAN + text + colorama.Style.RESET_ALL


def text_magenta(text: str) -> str:
    return colorama.Fore.MAGENTA + text + colorama.Style.RESET_ALL


class ViewportUnitConverter:
    """Convert between pixel/cm to ndc units in a viewport."""

    def __init__(self, canvas: Canvas, viewport: Viewport) -> None:
        """Initialize the converter with a canvas and viewport."""
        self._canvas = canvas
        self._viewport = viewport

    def get_canvas(self) -> Canvas:
        """Get the canvas."""
        return self._canvas

    def get_viewport(self) -> Viewport:
        """Get the viewport."""
        return self._viewport

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

    def delta_pixel_to_ndc(self, delta_pixel_x: float, delta_pixel_y: float) -> tuple[float, float]:
        """Convert a delta in pixels to a delta in NDC units."""
        viewport_range_ndc_x = 2.0
        viewport_range_ndc_y = 2.0

        delta_ndc_x = (delta_pixel_x / self._get_viewport_width_px()) * viewport_range_ndc_x
        delta_ndc_y = (delta_pixel_y / self._get_viewport_height_px()) * viewport_range_ndc_y

        return (delta_ndc_x, delta_ndc_y)

    def delta_cm_to_ndc(self, delta_cm_x: float, delta_cm_y: float) -> tuple[float, float]:
        """Convert a delta in cm to a delta in NDC units."""
        viewport_range_ndc_x = 2.0
        viewport_range_ndc_y = 2.0

        delta_ndc_x = (delta_cm_x / self._get_viewport_width_cm()) * viewport_range_ndc_x
        delta_ndc_y = (delta_cm_y / self._get_viewport_height_cm()) * viewport_range_ndc_y

        return (delta_ndc_x, delta_ndc_y)


@dataclass
class RenderItem:
    viewport: Viewport
    visual_base: VisualBase
    model_matrix: Buffer
    camera: Camera


from gsp.core import Event
from typing import Protocol


class AxesDisplayNewLimitsEventCallback(Protocol):
    """Protocol for axes display new limits event callback functions."""

    def __call__(self) -> None:
        """Handle a new limits event."""
        ...


class AxesDisplay:
    """Class to display axes in a viewport using NDC conversions."""

    def __init__(self, canvas: Canvas, inner_viewport: Viewport) -> None:
        """Initialize the AxesDisplay example."""
        self._canvas = canvas
        """Canvas to render on."""
        self._inner_viewport = inner_viewport
        """Innert viewport to render visual in."""
        self._outter_viewport = Viewport(0, 0, self._canvas.get_width(), self._canvas.get_height())
        """Outter viewport to render axes in (arround inner viewport)."""

        self._inner_viewport_unit = ViewportUnitConverter(self._canvas, self._inner_viewport)
        """Unit converter for inner viewport."""
        self._outter_viewport_unit = ViewportUnitConverter(self._canvas, self._outter_viewport)
        """Unit converter for outter viewport."""
        self._x_min = -1.0
        """x minimum in data units."""
        self._x_max = +1.0
        """x maximum in data units."""
        self._y_min = -1.0
        """y minimum in data units."""
        self._y_max = +1.0
        """y maximum in data units."""

        self.new_limits_event = Event[AxesDisplayNewLimitsEventCallback]()

        self._axes_segments_render_item: RenderItem | None = None
        self._ticks_horizontal_render_item: RenderItem | None = None
        self._ticks_vertical_render_item: RenderItem | None = None
        self._texts_horizontal_render_item: RenderItem | None = None
        self._texts_vertical_render_item: RenderItem | None = None

        self._build_render_items()

    def set_limits_data_space(self, x_min: float, x_max: float, y_min: float, y_max: float) -> None:
        """Set the axes limits in data units."""
        # sanity checks
        assert x_min < x_max, f"x_min MUST be less than x_max, got x_min={x_min}, x_max={x_max}"
        assert y_min < y_max, f"y_min MUST be less than y_max, got y_min={y_min}, y_max={y_max}"

        # set limits
        self._x_min = x_min
        self._x_max = x_max
        self._y_min = y_min
        self._y_max = y_max

        # rebuild render items
        self._build_render_items()

        # Notify event listeners
        self.new_limits_event.dispatch()

    def get_limits_data_space(self) -> tuple[float, float, float, float]:
        """Get the axes limits in data units."""
        return (self._x_min, self._x_max, self._y_min, self._y_max)

    def get_transform_matrix(self) -> np.ndarray:
        # Compute translation matrix
        translation_matrix = glm.translate(np.array([-(self._x_max + self._x_min) / 2.0, -(self._y_max + self._y_min) / 2.0, 0.0]))
        # Compute scale matrix
        scale_matrix = glm.scale(np.array([2.0 / (self._x_max - self._x_min), 2.0 / (self._y_max - self._y_min), 1.0]))
        # Combine translation and scale to get the final transform matrix
        axes_transform_numpy = scale_matrix @ translation_matrix
        # Return the transform matrix
        return axes_transform_numpy

    def get_inner_viewport(self) -> Viewport:
        """Get the inner viewport."""
        return self._inner_viewport

    def get_outter_viewport(self) -> Viewport:
        """Get the outter viewport."""
        return self._outter_viewport

    def get_render_items(self) -> list[RenderItem]:
        """Get the render items for the axes display."""
        render_items: list[RenderItem] = []

        # sanity check
        assert self._axes_segments_render_item is not None, "Axes segments render item MUST be initialized"
        assert self._ticks_horizontal_render_item is not None, "Ticks horizontal render item MUST be initialized"
        assert self._ticks_vertical_render_item is not None, "Ticks vertical render item MUST be initialized"
        assert self._texts_horizontal_render_item is not None, "Texts horizontal render item MUST be initialized"
        assert self._texts_vertical_render_item is not None, "Texts vertical render item MUST be initialized"

        render_items.append(self._axes_segments_render_item)
        render_items.append(self._ticks_horizontal_render_item)
        render_items.append(self._ticks_vertical_render_item)
        render_items.append(self._texts_horizontal_render_item)
        render_items.append(self._texts_vertical_render_item)

        return render_items

    # =============================================================================
    #
    # =============================================================================

    def _build_render_items(self) -> None:
        """Build the render items for the axes display."""
        # Create axes segments
        # =============================================================================
        #
        # =============================================================================
        axes_segments_uuid: str | None = self._axes_segments_render_item.visual_base.get_uuid() if self._axes_segments_render_item is not None else None
        self._axes_segments_render_item = RenderItem(
            self._outter_viewport_unit.get_viewport(),
            AxesDisplay._generate_axes_segments(self._inner_viewport_unit, self._outter_viewport_unit),
            Bufferx.mat4_identity(),
            Camera(Bufferx.mat4_identity(), Bufferx.mat4_identity()),
        )
        if axes_segments_uuid is not None:
            self._axes_segments_render_item.visual_base.set_uuid(axes_segments_uuid)

        # =============================================================================
        #
        # =============================================================================
        ticks_horizontal_uuid: str | None = (
            self._ticks_horizontal_render_item.visual_base.get_uuid() if self._ticks_horizontal_render_item is not None else None
        )
        self._ticks_horizontal_render_item = RenderItem(
            self._outter_viewport_unit.get_viewport(),
            AxesDisplay._generate_ticks_horizontal(self._inner_viewport_unit, self._outter_viewport_unit, self._x_min, self._x_max),
            Bufferx.mat4_identity(),
            Camera(Bufferx.mat4_identity(), Bufferx.mat4_identity()),
        )
        if ticks_horizontal_uuid is not None:
            self._ticks_horizontal_render_item.visual_base.set_uuid(ticks_horizontal_uuid)

        # =============================================================================
        #
        # =============================================================================
        ticks_vertical_uuid: str | None = self._ticks_vertical_render_item.visual_base.get_uuid() if self._ticks_vertical_render_item is not None else None
        self._ticks_vertical_render_item = RenderItem(
            self._outter_viewport_unit.get_viewport(),
            AxesDisplay._generate_ticks_vertical(self._inner_viewport_unit, self._outter_viewport_unit, self._y_min, self._y_max),
            Bufferx.mat4_identity(),
            Camera(Bufferx.mat4_identity(), Bufferx.mat4_identity()),
        )
        if ticks_vertical_uuid is not None:
            self._ticks_vertical_render_item.visual_base.set_uuid(ticks_vertical_uuid)

        # =============================================================================
        #
        # =============================================================================
        texts_horizontal_uuid: str | None = (
            self._texts_horizontal_render_item.visual_base.get_uuid() if self._texts_horizontal_render_item is not None else None
        )
        self._texts_horizontal_render_item = RenderItem(
            self._outter_viewport_unit.get_viewport(),
            AxesDisplay._generate_texts_horizontal(self._inner_viewport_unit, self._outter_viewport_unit, self._x_min, self._x_max),
            Bufferx.mat4_identity(),
            Camera(Bufferx.mat4_identity(), Bufferx.mat4_identity()),
        )
        if texts_horizontal_uuid is not None:
            self._texts_horizontal_render_item.visual_base.set_uuid(texts_horizontal_uuid)

        # =============================================================================
        #
        # =============================================================================
        texts_vertical_uuid: str | None = self._texts_vertical_render_item.visual_base.get_uuid() if self._texts_vertical_render_item is not None else None
        self._texts_vertical_render_item = RenderItem(
            self._outter_viewport_unit.get_viewport(),
            AxesDisplay._generate_texts_vertical(self._inner_viewport_unit, self._outter_viewport_unit, self._y_min, self._y_max),
            Bufferx.mat4_identity(),
            Camera(Bufferx.mat4_identity(), Bufferx.mat4_identity()),
        )
        if texts_vertical_uuid is not None:
            self._texts_vertical_render_item.visual_base.set_uuid(texts_vertical_uuid)

    @staticmethod
    def _generate_axes_segments(inner_viewport_unit: ViewportUnitConverter, outter_viewport_unit: ViewportUnitConverter) -> Segments:
        """Generate axes segments in NDC units for the given viewport."""
        inner_viewport = inner_viewport_unit.get_viewport()
        canvas = inner_viewport_unit.get_canvas()

        # Compute NDC coordinates of the inner viewport corners in outter viewport
        delta_min_ndc = outter_viewport_unit.delta_pixel_to_ndc(inner_viewport.get_x(), inner_viewport.get_y())
        delta_max_ndc = outter_viewport_unit.delta_pixel_to_ndc(
            inner_viewport.get_x() + inner_viewport.get_width(),
            inner_viewport.get_y() + inner_viewport.get_height(),
        )
        coord_min_ndc = (-1.0 + delta_min_ndc[0], -1.0 + delta_min_ndc[1])
        coord_max_ndc = (-1.0 + delta_max_ndc[0], -1.0 + delta_max_ndc[1])

        # Create segments for the axes
        segments_count = 2
        positions_numpy = np.array(
            [
                [coord_min_ndc[0], coord_min_ndc[1], 0.0],
                [coord_max_ndc[0], coord_min_ndc[1], 0.0],
                [coord_min_ndc[0], coord_min_ndc[1], 0.0],
                [coord_min_ndc[0], coord_max_ndc[1], 0.0],
            ],
            dtype=np.float32,
        )
        positions_buffer = Bufferx.from_numpy(positions_numpy, BufferType.vec3)

        line_widths_numpy = np.array([UnitUtils.pixel_to_point(2, canvas.get_dpi())] * segments_count, dtype=np.float32)
        line_widths_buffer = Bufferx.from_numpy(line_widths_numpy, BufferType.float32)

        colors_buffer = Buffer(segments_count, BufferType.rgba8)
        colors_buffer.set_data(Constants.Color.black * segments_count, 0, segments_count)

        segments = Segments(positions_buffer, line_widths_buffer, CapStyle.ROUND, colors_buffer)
        return segments

    @staticmethod
    def _generate_ticks_horizontal(
        inner_viewport_unit: ViewportUnitConverter,
        outter_viewport_unit: ViewportUnitConverter,
        x_min_data_space: float,
        x_max_data_space: float,
    ) -> Segments:
        inner_viewport = inner_viewport_unit.get_viewport()
        canvas = outter_viewport_unit.get_canvas()

        # Create positions for ticks from -num_ticks/2 to +num_ticks/2
        positions_array = []
        for tick_x_inner_data_space in range(math.ceil(x_min_data_space), math.ceil(x_max_data_space) + 1):
            # skip ticks outside data space limits
            if tick_x_inner_data_space > x_max_data_space:
                continue

            # compute tick_x_outter_ndc
            tick_x_inner_ndc = (tick_x_inner_data_space - x_min_data_space) / (x_max_data_space - x_min_data_space) * 2.0 - 1.0
            tick_x_outter_delta_pixel = inner_viewport.get_x() + ((tick_x_inner_ndc + 1.0) / 2.0) * inner_viewport.get_width()
            tick_x_outter_delta_ndc, _ = outter_viewport_unit.delta_pixel_to_ndc(tick_x_outter_delta_pixel, 0.0)
            tick_x_outter_ndc = tick_x_outter_delta_ndc - 1.0

            # compute tick_y_outter_ndc
            tick_y_inner_ndc = -1.0  # at bottom of inner viewport
            tick_y_outter_pixel = inner_viewport.get_y() + ((tick_y_inner_ndc + 1.0) / 2.0) * inner_viewport.get_height()
            _, tick_y_outter_delta_ndc = outter_viewport_unit.delta_pixel_to_ndc(0.0, tick_y_outter_pixel)
            tick_y_outter_ndc = tick_y_outter_delta_ndc - 1.0

            # compute tick_height_ndc
            _, tick_height_ndc = outter_viewport_unit.delta_cm_to_ndc(0.0, 0.2)

            positions_array.append([tick_x_outter_ndc, tick_y_outter_ndc + 0.0, 0.0])
            positions_array.append([tick_x_outter_ndc, tick_y_outter_ndc - tick_height_ndc, 0.0])

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

        segments = Segments(positions_buffer, line_widths_buffer, CapStyle.ROUND, colors_buffer)
        return segments

    @staticmethod
    def _generate_ticks_vertical(
        inner_viewport_unit: ViewportUnitConverter,
        outter_viewport_unit: ViewportUnitConverter,
        y_min_data_space: float,
        y_max_data_space: float,
    ) -> Segments:
        inner_viewport = inner_viewport_unit.get_viewport()
        canvas = outter_viewport_unit.get_canvas()

        # Create positions for ticks from -num_ticks/2 to +num_ticks/2
        positions_array = []
        for tick_y_inner_data_space in range(math.ceil(y_min_data_space), math.ceil(y_max_data_space) + 1):
            # skip ticks outside data space limits
            if tick_y_inner_data_space > y_max_data_space:
                continue

            # compute tick_y_outter_ndc
            tick_y_inner_ndc = (tick_y_inner_data_space - y_min_data_space) / (y_max_data_space - y_min_data_space) * 2.0 - 1.0
            tick_y_outter_delta_pixel = inner_viewport.get_y() + ((tick_y_inner_ndc + 1.0) / 2.0) * inner_viewport.get_height()
            tick_y_outter_delta_ndc, _ = outter_viewport_unit.delta_pixel_to_ndc(tick_y_outter_delta_pixel, 0.0)
            tick_y_outter_ndc = tick_y_outter_delta_ndc - 1.0

            # compute tick_y_outter_ndc
            tick_x_inner_ndc = -1.0  # at bottom of inner viewport
            tick_x_outter_pixel = inner_viewport.get_x() + ((tick_x_inner_ndc + 1.0) / 2.0) * inner_viewport.get_width()
            _, tick_x_outter_delta_ndc = outter_viewport_unit.delta_pixel_to_ndc(0.0, tick_x_outter_pixel)
            tick_x_outter_ndc = tick_x_outter_delta_ndc - 1.0

            # compute tick_height_ndc
            tick_width_ndc, _ = outter_viewport_unit.delta_cm_to_ndc(0.2, 0.0)

            positions_array.append([tick_x_outter_ndc, tick_y_outter_ndc + 0.0, 0.0])
            positions_array.append([tick_x_outter_ndc - tick_width_ndc, tick_y_outter_ndc, 0.0])

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

    @staticmethod
    def _generate_texts_horizontal(
        inner_viewport_unit: ViewportUnitConverter,
        outter_viewport_unit: ViewportUnitConverter,
        x_min_data_space: float,
        x_max_data_space: float,
    ) -> Texts:
        inner_viewport = inner_viewport_unit.get_viewport()
        canvas = outter_viewport_unit.get_canvas()

        # Create positions for ticks from -num_ticks/2 to +num_ticks/2
        positions_array = []
        for tick_x_inner_data_space in range(math.ceil(x_min_data_space), math.ceil(x_max_data_space) + 1):
            # skip ticks outside data space limits
            if tick_x_inner_data_space > x_max_data_space:
                continue

            # compute tick_x_outter_ndc
            tick_x_inner_ndc = (tick_x_inner_data_space - x_min_data_space) / (x_max_data_space - x_min_data_space) * 2.0 - 1.0
            tick_x_outter_delta_pixel = inner_viewport.get_x() + ((tick_x_inner_ndc + 1.0) / 2.0) * inner_viewport.get_width()
            tick_x_outter_delta_ndc, _ = outter_viewport_unit.delta_pixel_to_ndc(tick_x_outter_delta_pixel, 0.0)
            tick_x_outter_ndc = tick_x_outter_delta_ndc - 1.0

            # compute tick_y_outter_ndc
            tick_y_inner_ndc = -1.0  # at bottom of inner viewport
            tick_y_outter_delta_pixel = inner_viewport.get_y() + ((tick_y_inner_ndc + 1.0) / 2.0) * inner_viewport.get_height()
            _, tick_y_outter_delta_ndc = outter_viewport_unit.delta_pixel_to_ndc(0.0, tick_y_outter_delta_pixel)
            tick_y_outter_ndc = tick_y_outter_delta_ndc - 1.0

            # compute tick_height_ndc
            _, tick_height_ndc = outter_viewport_unit.delta_cm_to_ndc(0.0, 0.3)

            positions_array.append([tick_x_outter_ndc, tick_y_outter_ndc - tick_height_ndc, 0.0])

        positions_numpy = np.array(positions_array, dtype=np.float32)
        positions_buffer = Bufferx.from_numpy(positions_numpy, BufferType.vec3)

        strings = []
        for tick_x_inner_data_space in range(math.ceil(x_min_data_space), math.ceil(x_max_data_space) + 1):
            # skip texts outside data space limits
            if tick_x_inner_data_space > x_max_data_space:
                continue

            strings.append(f"{tick_x_inner_data_space}")
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

    @staticmethod
    def _generate_texts_vertical(
        inner_viewport_unit: ViewportUnitConverter,
        outter_viewport_unit: ViewportUnitConverter,
        y_min_data_space: float,
        y_max_data_space: float,
    ) -> Texts:
        inner_viewport = inner_viewport_unit.get_viewport()
        canvas = outter_viewport_unit.get_canvas()

        # Create positions for ticks from -num_ticks/2 to +num_ticks/2
        positions_array = []
        for tick_y_inner_data_space in range(math.ceil(y_min_data_space), math.ceil(y_max_data_space) + 1):
            # skip texts outside data space limits
            if tick_y_inner_data_space > y_max_data_space:
                continue

            # compute tick_y_outter_ndc
            tick_y_inner_ndc = (tick_y_inner_data_space - y_min_data_space) / (y_max_data_space - y_min_data_space) * 2.0 - 1.0
            tick_y_outter_delta_pixel = inner_viewport.get_y() + ((tick_y_inner_ndc + 1.0) / 2.0) * inner_viewport.get_height()
            tick_y_outter_delta_ndc, _ = outter_viewport_unit.delta_pixel_to_ndc(tick_y_outter_delta_pixel, 0.0)
            tick_y_outter_ndc = tick_y_outter_delta_ndc - 1.0

            # compute tick_y_outter_ndc
            tick_x_inner_ndc = -1.0  # at bottom of inner viewport
            tick_x_outter_pixel = inner_viewport.get_x() + ((tick_x_inner_ndc + 1.0) / 2.0) * inner_viewport.get_width()
            _, tick_x_outter_delta_ndc = outter_viewport_unit.delta_pixel_to_ndc(0.0, tick_x_outter_pixel)
            tick_x_outter_ndc = tick_x_outter_delta_ndc - 1.0

            # compute tick_height_ndc
            tick_width_ndc, _ = outter_viewport_unit.delta_cm_to_ndc(0.3, 0.0)

            positions_array.append([tick_x_outter_ndc - tick_width_ndc, tick_y_outter_ndc, 0.0])

        positions_numpy = np.array(positions_array, dtype=np.float32)
        positions_buffer = Bufferx.from_numpy(positions_numpy, BufferType.vec3)

        strings = []
        for tick_y_inner_data_space in range(math.ceil(y_min_data_space), math.ceil(y_max_data_space) + 1):
            # skip texts outside data space limits
            if tick_y_inner_data_space > y_max_data_space:
                continue
            strings.append(f"{tick_y_inner_data_space}")
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


class AxesPanZoom:
    """Class to handle panning and zooming in a viewport."""

    def __init__(self, viewport_events: ViewportEventsBase, base_scale: float, axes_display: AxesDisplay) -> None:
        """Initialize the PanAndZoom example."""
        self._viewport_events = viewport_events
        """Viewport events to listen to."""
        self._base_scale = base_scale
        """Base scale for zooming."""
        self._axes_display = axes_display
        """Axes display to update."""

        self._button_press_x: float | None = None
        """X coordinate of the button press in NDC units."""
        self._button_press_y: float | None = None
        """Y coordinate of the button press in NDC units."""

        self._x_min_data_space: float | None = None
        """Current x minimum viewport in data space."""
        self._x_max_data_space: float | None = None
        """Current x maximum viewport in data space."""
        self._y_min_data_space: float | None = None
        """Current y minimum viewport in data space."""
        self._y_max_data_space: float | None = None
        """Current y maximum viewport in data space."""

        self._viewport_events.button_press_event.subscribe(self._on_button_press)
        self._viewport_events.button_release_event.subscribe(self._on_button_release)
        self._viewport_events.mouse_move_event.subscribe(self._on_button_move)
        self._viewport_events.mouse_scroll_event.subscribe(self._on_mouse_scroll)

    def close(self) -> None:
        """Close the PanAndZoom example."""
        self._viewport_events.button_press_event.unsubscribe(self._on_button_press)
        self._viewport_events.button_release_event.unsubscribe(self._on_button_release)
        self._viewport_events.mouse_move_event.unsubscribe(self._on_button_move)
        self._viewport_events.mouse_scroll_event.unsubscribe(self._on_mouse_scroll)

    def _on_button_press(self, mouse_event: MouseEvent):
        # print(f"{text_cyan('Button press')}: {text_magenta(mouse_event.viewport_uuid)} {mouse_event}")
        # Store pixel coordinates instead of data coordinates
        self._button_press_x = mouse_event.x
        self._button_press_y = mouse_event.y

        self._x_min_data_space, self._x_max_data_space, self._y_min_data_space, self._y_max_data_space = self._axes_display.get_limits_data_space()

    def _on_button_release(self, mouse_event: MouseEvent):
        # print(f"{text_cyan('Button release')}: {text_magenta(mouse_event.viewport_uuid)} {mouse_event}")
        self._button_press_x = None
        self._button_press_y = None
        self._x_min_data_space = None
        self._x_max_data_space = None
        self._y_min_data_space = None
        self._y_max_data_space = None

    def _on_button_move(self, mouse_event: MouseEvent):
        # print(f"{text_cyan('Button move')}: {text_magenta(mouse_event.viewport_uuid)} {mouse_event}")
        if self._button_press_x is None or self._button_press_y is None:
            return
        if self._x_min_data_space is None or self._x_max_data_space is None or self._y_min_data_space is None or self._y_max_data_space is None:
            return

        # Calculate the delta in NDC units
        delta_x_ndc: float = mouse_event.x - self._button_press_x
        delta_y_ndc: float = mouse_event.y - self._button_press_y

        # Compute new limits in data space for the viewports
        new_x_min_data_space: float = self._x_min_data_space - (delta_x_ndc / 2.0) * (self._x_max_data_space - self._x_min_data_space)
        new_x_max_data_space: float = self._x_max_data_space - (delta_x_ndc / 2.0) * (self._x_max_data_space - self._x_min_data_space)
        new_y_min_data_space: float = self._y_min_data_space - (delta_y_ndc / 2.0) * (self._y_max_data_space - self._y_min_data_space)
        new_y_max_data_space: float = self._y_max_data_space - (delta_y_ndc / 2.0) * (self._y_max_data_space - self._y_min_data_space)

        # Update the axes limits in data space
        self._axes_display.set_limits_data_space(new_x_min_data_space, new_x_max_data_space, new_y_min_data_space, new_y_max_data_space)

    def _on_mouse_scroll(self, mouse_event: MouseEvent):
        # print(f"{text_cyan('Mouse scroll')}: {text_magenta(mouse_event.viewport_uuid)} {mouse_event}")

        scale_factor: float = 1 / self._base_scale if mouse_event.scroll_steps >= 0 else self._base_scale

        x_min_data_space, x_max_data_space, y_min_data_space, y_max_data_space = self._axes_display.get_limits_data_space()

        print(f"scale_factor: {scale_factor}")

        mouse_x_dataspace: float = x_min_data_space + (mouse_event.x + 1.0) / 2.0 * (x_max_data_space - x_min_data_space)
        mouse_y_dataspace: float = y_min_data_space + (mouse_event.y + 1.0) / 2.0 * (y_max_data_space - y_min_data_space)

        new_width: float = (x_max_data_space - x_min_data_space) * scale_factor
        new_height: float = (y_max_data_space - y_min_data_space) * scale_factor
        relative_x: float = (x_max_data_space - mouse_x_dataspace) / (x_max_data_space - x_min_data_space)
        relative_y: float = (y_max_data_space - mouse_y_dataspace) / (y_max_data_space - y_min_data_space)

        new_x_min: float = mouse_x_dataspace - new_width * (1 - relative_x)
        new_x_max: float = mouse_x_dataspace + new_width * (relative_x)
        new_y_min: float = mouse_y_dataspace - new_height * (1 - relative_y)
        new_y_max: float = mouse_y_dataspace + new_height * (relative_y)

        self._axes_display.set_limits_data_space(new_x_min, new_x_max, new_y_min, new_y_max)

        print(f"New limits: x[{new_x_min}, {new_x_max}] y[{new_y_min}, {new_y_max}]")


def main():
    """Example demonstrating viewport NDC metric conversions."""
    # fix random seed for reproducibility
    np.random.seed(0)

    # Create a canvas
    canvas = Canvas(width=400, height=400, dpi=127)

    # =============================================================================
    #
    # =============================================================================

    # Create a inner viewport
    inner_viewport = Viewport(int(canvas.get_width() / 4), int(canvas.get_height() / 4), int(canvas.get_width() / 2), int(canvas.get_height() / 2))
    # inner_viewport = Viewport(int(canvas.get_width() * 0.1), int(canvas.get_height() * 0.1), int(canvas.get_width() * 0.8), int(canvas.get_height() * 0.8))
    # inner_viewport = Viewport(int(canvas.get_width() / 3), int(canvas.get_height() / 4), int(canvas.get_width() / 3), int(canvas.get_height() / 2))

    axes_display = AxesDisplay(canvas, inner_viewport)
    axes_display.set_limits_data_space(-1.0, +1.0, -1.0, +1.0)
    render_items_axes = axes_display.get_render_items()

    renderer_name = ExampleHelper.get_renderer_name()
    renderer_base = ExampleHelper.create_renderer(renderer_name, canvas)

    viewport_events = ExampleHelper.create_viewport_events(renderer_base, axes_display.get_inner_viewport())
    axes_pan_zoom = AxesPanZoom(viewport_events, base_scale=1.1, axes_display=axes_display)

    # =============================================================================
    #
    # =============================================================================

    def generate_visual_points(point_count: int, viewport: Viewport, axes_transform_numpy: np.ndarray) -> list[RenderItem]:
        # Generate a sinusoidal distribution of points
        x_values = np.linspace(-1.0, +1.0, point_count, dtype=np.float32)
        y_values = np.sin(x_values * np.pi).astype(np.float32)
        z_values = np.zeros(point_count, dtype=np.float32)
        positions_numpy = np.vstack((x_values, y_values, z_values)).T.astype(np.float32)

        # positions_numpy = np.random.rand(point_count, 3).astype(np.float32) * 2.0 - 1
        positions_buffer = Bufferx.from_numpy(positions_numpy, BufferType.vec3)

        # Sizes - Create buffer and set data with numpy array
        sizes_numpy = np.array([10] * point_count, dtype=np.float32)
        sizes_buffer = Bufferx.from_numpy(sizes_numpy, BufferType.float32)

        # all pixels red - Create buffer and fill it with a constant
        face_colors_buffer = Buffer(point_count, BufferType.rgba8)
        face_colors_buffer.set_data(bytearray([255, 0, 0, 255]) * point_count, 0, point_count)

        # Edge colors - Create buffer and fill it with a constant
        edge_colors_buffer = Buffer(point_count, BufferType.rgba8)
        edge_colors_buffer.set_data(Constants.Color.blue * point_count, 0, point_count)

        # Edge widths - Create buffer and fill it with a constant
        edge_widths_numpy = np.array([UnitUtils.pixel_to_point(1, canvas.get_dpi())] * point_count, dtype=np.float32)
        edge_widths_buffer = Bufferx.from_numpy(edge_widths_numpy, BufferType.float32)

        # Create the Points visual and add it to the viewport
        points = Points(positions_buffer, sizes_buffer, face_colors_buffer, edge_colors_buffer, edge_widths_buffer)

        # Create model matrix to transform points into axes data space
        model_matrix_numpy = np.eye(4, dtype=np.float32)
        model_matrix_numpy = axes_transform_numpy @ model_matrix_numpy
        model_matrix = Bufferx.from_numpy(np.array([model_matrix_numpy]), BufferType.mat4)

        # model_matrix = Bufferx.mat4_identity()

        camera = Camera(Bufferx.mat4_identity(), Bufferx.mat4_identity())

        render_items: list[RenderItem] = []
        render_items.append(RenderItem(viewport, points, model_matrix, camera))
        return render_items

    axes_transform_numpy = axes_display.get_transform_matrix()
    render_items_points = generate_visual_points(100, inner_viewport, axes_transform_numpy)

    # =============================================================================
    #
    # =============================================================================

    render_items = render_items_points + render_items_axes
    # render_items = render_items_axes

    # =============================================================================
    #
    # =============================================================================
    def on_new_limits():
        print(f"{text_cyan('New limits event received')}")
        axes_transform_numpy = axes_display.get_transform_matrix()

        for render_item in render_items_points:
            model_matrix_numpy = np.eye(4, dtype=np.float32)
            model_matrix_numpy = axes_transform_numpy @ model_matrix_numpy
            render_item.model_matrix = Bufferx.from_numpy(np.array([model_matrix_numpy]), BufferType.mat4)

        render_items_axes = axes_display.get_render_items()
        render_items = render_items_points + render_items_axes

        renderer_base.render(
            [render_item.viewport for render_item in render_items],
            [render_item.visual_base for render_item in render_items],
            [render_item.model_matrix for render_item in render_items],
            [render_item.camera for render_item in render_items],
        )

    axes_display.new_limits_event.subscribe(on_new_limits)
    on_new_limits()
    # =============================================================================
    #
    # =============================================================================

    # renderer_base.render(
    #     [render_item.viewport for render_item in render_items],
    #     [render_item.visual_base for render_item in render_items],
    #     [render_item.model_matrix for render_item in render_items],
    #     [render_item.camera for render_item in render_items],
    # )

    # =============================================================================
    #
    # =============================================================================
    # renderer_base.show()

    animator = ExampleHelper.create_animator(renderer_base)

    # @animator.event_listener
    # def animator_callback(delta_time: float) -> list[VisualBase]:
    #     # print(f"{text_cyan('Animator callback')}: delta_time={delta_time:.4f} sec")

    #     changed_visuals: list[VisualBase] = []
    #     return changed_visuals

    # start the animation loop
    animator.start(
        [],
        [],
        [],
        [],
        # [render_item.viewport for render_item in render_items],
        # [render_item.visual_base for render_item in render_items],
        # [render_item.model_matrix for render_item in render_items],
        # [render_item.camera for render_item in render_items],
    )


if __name__ == "__main__":
    main()
