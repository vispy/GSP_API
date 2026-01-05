"""Module providing an AxesDisplay class to display axes in a viewport using NDC conversions."""

# stdlib imports
import math
from typing import Protocol

# pip imports
import numpy as np

# local imports
from gsp.core import Canvas, Viewport, Event
from gsp.core.camera import Camera
from gsp.visuals import Segments, Texts
from gsp.types import CapStyle
from gsp.types import BufferType
from gsp.types import Buffer
from gsp.constants import Constants
from gsp.utils.unit_utils import UnitUtils
from gsp.utils.viewport_unit_utils import ViewportUnitUtils
from gsp_extra.mpl3d import glm
from gsp_extra.misc.render_item import RenderItem
from gsp_extra.bufferx import Bufferx


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

        self._inner_viewport_unit = ViewportUnitUtils(self._canvas, self._inner_viewport)
        """Unit converter for inner viewport."""
        self._outter_viewport_unit = ViewportUnitUtils(self._canvas, self._outter_viewport)
        """Unit converter for outter viewport."""
        self._x_min_dunit = -1.0
        """x minimum in data units."""
        self._x_max_dunit = +1.0
        """x maximum in data units."""
        self._y_min_dunit = -1.0
        """y minimum in data units."""
        self._y_max_dunit = +1.0
        """y maximum in data units."""

        self.new_limits_event = Event[AxesDisplayNewLimitsEventCallback]()
        """Event triggered when the axes limits are changed.
        
        Allow to render visuals and axes synchronously when axes limits change.
        """

        # Initialize render items
        self._axes_segments_render_item: RenderItem | None = None
        self._ticks_horizontal_render_item: RenderItem | None = None
        self._ticks_vertical_render_item: RenderItem | None = None
        self._texts_horizontal_render_item: RenderItem | None = None
        self._texts_vertical_render_item: RenderItem | None = None

        # Build render items
        self._build_render_items()

    def set_limits_dunit(self, x_min_dunit: float, x_max_dunit: float, y_min_dunit: float, y_max_dunit: float) -> None:
        """Set the axes limits in data units."""
        # sanity checks
        assert x_min_dunit < x_max_dunit, f"x_min MUST be less than x_max, got x_min_dunit={x_min_dunit}, x_max_dunit={x_max_dunit}"
        assert y_min_dunit < y_max_dunit, f"y_min MUST be less than y_max, got y_min_dunit={y_min_dunit}, y_max_dunit={y_max_dunit}"

        # set limits
        self._x_min_dunit = x_min_dunit
        self._x_max_dunit = x_max_dunit
        self._y_min_dunit = y_min_dunit
        self._y_max_dunit = y_max_dunit

        # rebuild render items
        self._build_render_items()

        # Notify event listeners
        self.new_limits_event.dispatch()

    def get_limits_dunit(self) -> tuple[float, float, float, float]:
        """Get the axes limits in data units."""
        return (self._x_min_dunit, self._x_max_dunit, self._y_min_dunit, self._y_max_dunit)

    def get_transform_matrix_numpy(self) -> np.ndarray:
        """Get the transform matrix from data units to NDC units for the inner viewport."""
        # Compute translation matrix
        translation_matrix = glm.translate(np.array([-(self._x_max_dunit + self._x_min_dunit) / 2.0, -(self._y_max_dunit + self._y_min_dunit) / 2.0, 0.0]))
        # Compute scale matrix
        scale_matrix = glm.scale(np.array([2.0 / (self._x_max_dunit - self._x_min_dunit), 2.0 / (self._y_max_dunit - self._y_min_dunit), 1.0]))
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
        # sanity check
        assert self._axes_segments_render_item is not None, "Axes segments render item MUST be initialized"
        assert self._ticks_horizontal_render_item is not None, "Ticks horizontal render item MUST be initialized"
        assert self._ticks_vertical_render_item is not None, "Ticks vertical render item MUST be initialized"
        assert self._texts_horizontal_render_item is not None, "Texts horizontal render item MUST be initialized"
        assert self._texts_vertical_render_item is not None, "Texts vertical render item MUST be initialized"

        # Collect all render items into a list
        render_items: list[RenderItem] = []
        render_items.append(self._axes_segments_render_item)
        render_items.append(self._ticks_horizontal_render_item)
        render_items.append(self._ticks_vertical_render_item)
        render_items.append(self._texts_horizontal_render_item)
        render_items.append(self._texts_vertical_render_item)

        # Retrun the render items
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
            AxesDisplay._generate_ticks_horizontal(self._inner_viewport_unit, self._outter_viewport_unit, self._x_min_dunit, self._x_max_dunit),
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
            AxesDisplay._generate_ticks_vertical(self._inner_viewport_unit, self._outter_viewport_unit, self._y_min_dunit, self._y_max_dunit),
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
            AxesDisplay._generate_texts_horizontal(self._inner_viewport_unit, self._outter_viewport_unit, self._x_min_dunit, self._x_max_dunit),
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
            AxesDisplay._generate_texts_vertical(self._inner_viewport_unit, self._outter_viewport_unit, self._y_min_dunit, self._y_max_dunit),
            Bufferx.mat4_identity(),
            Camera(Bufferx.mat4_identity(), Bufferx.mat4_identity()),
        )
        if texts_vertical_uuid is not None:
            self._texts_vertical_render_item.visual_base.set_uuid(texts_vertical_uuid)

    @staticmethod
    def _generate_axes_segments(inner_viewport_unit: ViewportUnitUtils, outter_viewport_unit: ViewportUnitUtils) -> Segments:
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
        inner_viewport_unit: ViewportUnitUtils,
        outter_viewport_unit: ViewportUnitUtils,
        x_min_dunit: float,
        x_max_dunit: float,
    ) -> Segments:
        inner_viewport = inner_viewport_unit.get_viewport()
        canvas = outter_viewport_unit.get_canvas()

        # Create positions for ticks from -num_ticks/2 to +num_ticks/2
        positions_array = []
        for tick_x_inner_dunit in range(math.ceil(x_min_dunit), math.ceil(x_max_dunit) + 1):
            # skip ticks outside data space limits
            if tick_x_inner_dunit > x_max_dunit:
                continue

            # compute tick_x_outter_ndc
            tick_x_inner_ndc = (tick_x_inner_dunit - x_min_dunit) / (x_max_dunit - x_min_dunit) * 2.0 - 1.0
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
        inner_viewport_unit: ViewportUnitUtils,
        outter_viewport_unit: ViewportUnitUtils,
        y_min_dunit: float,
        y_max_dunit: float,
    ) -> Segments:
        inner_viewport = inner_viewport_unit.get_viewport()
        canvas = outter_viewport_unit.get_canvas()

        # Create positions for ticks from -num_ticks/2 to +num_ticks/2
        positions_array = []
        for tick_y_inner_dunit in range(math.ceil(y_min_dunit), math.ceil(y_max_dunit) + 1):
            # skip ticks outside data space limits
            if tick_y_inner_dunit > y_max_dunit:
                continue

            # compute tick_y_outter_ndc
            tick_y_inner_ndc = (tick_y_inner_dunit - y_min_dunit) / (y_max_dunit - y_min_dunit) * 2.0 - 1.0
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
        inner_viewport_unit: ViewportUnitUtils,
        outter_viewport_unit: ViewportUnitUtils,
        x_min_dunit: float,
        x_max_dunit: float,
    ) -> Texts:
        inner_viewport = inner_viewport_unit.get_viewport()
        canvas = outter_viewport_unit.get_canvas()

        # Create positions for ticks from -num_ticks/2 to +num_ticks/2
        positions_array = []
        for tick_x_inner_dunit in range(math.ceil(x_min_dunit), math.ceil(x_max_dunit) + 1):
            # skip ticks outside data space limits
            if tick_x_inner_dunit > x_max_dunit:
                continue

            # compute tick_x_outter_ndc
            tick_x_inner_ndc = (tick_x_inner_dunit - x_min_dunit) / (x_max_dunit - x_min_dunit) * 2.0 - 1.0
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
        for tick_x_inner_dunit in range(math.ceil(x_min_dunit), math.ceil(x_max_dunit) + 1):
            # skip texts outside data space limits
            if tick_x_inner_dunit > x_max_dunit:
                continue

            strings.append(f"{tick_x_inner_dunit}")
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
        inner_viewport_unit: ViewportUnitUtils,
        outter_viewport_unit: ViewportUnitUtils,
        y_min_dunit: float,
        y_max_dunit: float,
    ) -> Texts:
        inner_viewport = inner_viewport_unit.get_viewport()
        canvas = outter_viewport_unit.get_canvas()

        # Create positions for ticks from -num_ticks/2 to +num_ticks/2
        positions_array = []
        for tick_y_inner_dunit in range(math.ceil(y_min_dunit), math.ceil(y_max_dunit) + 1):
            # skip texts outside data space limits
            if tick_y_inner_dunit > y_max_dunit:
                continue

            # compute tick_y_outter_ndc
            tick_y_inner_ndc = (tick_y_inner_dunit - y_min_dunit) / (y_max_dunit - y_min_dunit) * 2.0 - 1.0
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
        for tick_y_inner_dunit in range(math.ceil(y_min_dunit), math.ceil(y_max_dunit) + 1):
            # skip texts outside data space limits
            if tick_y_inner_dunit > y_max_dunit:
                continue
            strings.append(f"{tick_y_inner_dunit}")
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
