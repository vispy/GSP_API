"""Class AxesPanZoom to handle panning and zooming in a viewport."""

# local imports
import math
from gsp.types.viewport_events_types import MouseEvent
from gsp.types.viewport_events_base import ViewportEventsBase
from .axes_display import AxesDisplay


class AxesPanZoom:
    """Class to handle panning and zooming in a viewport."""

    def __init__(self, viewport_events: ViewportEventsBase, base_scale: float, axes_display: AxesDisplay) -> None:
        """Initialize the PanAndZoom example."""
        self._viewport_events = viewport_events
        """Viewport events to listen to."""
        self._base_scale = base_scale
        """Base scale for zooming. Greater than 1.0. E.g., 1.1 means 10% zoom in/out per scroll step."""
        self._axes_display = axes_display
        """Axes display to update."""

        # Store state for panning
        self._button_press_x_ndc: float | None = None
        """X coordinate of the button press in NDC units."""
        self._button_press_y_ndc: float | None = None
        """Y coordinate of the button press in NDC units."""

        # Store initial limits for this axes
        self._x_min_dunit: float | None = None
        """Current x minimum viewport in data units."""
        self._x_max_dunit: float | None = None
        """Current x maximum viewport in data units."""
        self._y_min_dunit: float | None = None
        """Current y minimum viewport in data units."""
        self._y_max_dunit: float | None = None
        """Current y maximum viewport in data units."""

        # Subscribe to viewport events
        self._viewport_events.button_press_event.subscribe(self._on_button_press)
        self._viewport_events.button_release_event.subscribe(self._on_button_release)
        self._viewport_events.mouse_move_event.subscribe(self._on_mouse_move)
        self._viewport_events.mouse_scroll_event.subscribe(self._on_mouse_scroll)

        # Zoom range limit in data units
        self._zoom_x_min_range_dunit: float | None = None
        """Minimum zoom range in data units for x axis."""
        self._zoom_y_min_range_dunit: float | None = None
        """Minimum zoom range in data units for y axis."""
        self._zoom_x_max_range_dunit: float | None = None
        """Maximum zoom range in data units for x axis."""
        self._zoom_y_max_range_dunit: float | None = None
        """Maximum zoom range in data units for y axis."""

        # Pan limits in data units
        self._pan_x_min_dunit: float | None = None
        """Minimum pan limit in data units for x axis."""
        self._pan_x_max_dunit: float | None = None
        """Maximum pan limit in data units for x axis."""
        self._pan_y_min_dunit: float | None = None
        """Minimum pan limit in data units for y axis."""
        self._pan_y_max_dunit: float | None = None
        """Maximum pan limit in data units for y axis."""

    def close(self) -> None:
        """Close the PanAndZoom example."""
        # Unsubscribe from viewport events
        self._viewport_events.button_press_event.unsubscribe(self._on_button_press)
        self._viewport_events.button_release_event.unsubscribe(self._on_button_release)
        self._viewport_events.mouse_move_event.unsubscribe(self._on_mouse_move)
        self._viewport_events.mouse_scroll_event.unsubscribe(self._on_mouse_scroll)

    # =============================================================================
    # Getters / setters for pan limit
    # =============================================================================

    def get_pan_limits_dunit(self) -> tuple[float | None, float | None, float | None, float | None]:
        """Get the pan limits in data units.

        Returns:
            tuple[float | None, float | None, float | None, float | None]: Pan limits for x min, x max, y min, y max in data units.
        """
        return self._pan_x_min_dunit, self._pan_x_max_dunit, self._pan_y_min_dunit, self._pan_y_max_dunit

    def set_pan_limits_dunit(self, x_min_dunit: float | None, x_max_dunit: float | None, y_min_dunit: float | None, y_max_dunit: float | None) -> None:
        """Set the pan limits in data units.

        Args:
            x_min_dunit (float | None): Minimum pan limit for x axis in data units. If None, no limit is applied.
            x_max_dunit (float | None): Maximum pan limit for x axis in data units. If None, no limit is applied.
            y_min_dunit (float | None): Minimum pan limit for y axis in data units. If None, no limit is applied.
            y_max_dunit (float | None): Maximum pan limit for y axis in data units. If None, no limit is applied.
        """
        self._pan_x_min_dunit = x_min_dunit
        self._pan_x_max_dunit = x_max_dunit
        self._pan_y_min_dunit = y_min_dunit
        self._pan_y_max_dunit = y_max_dunit

    # =============================================================================
    # getters / setters zoom range limit
    # =============================================================================

    def get_zoom_range_limits_dunit(self) -> tuple[float | None, float | None, float | None, float | None]:
        """Get the zoom range limits in data units.

        Returns:
            tuple[float | None, float | None, float | None, float | None]: Min and max zoom range for x and y axes in data units.
        """
        return (self._zoom_x_min_range_dunit, self._zoom_x_max_range_dunit, self._zoom_y_min_range_dunit, self._zoom_y_max_range_dunit)

    def set_zoom_range_limits_dunit(
        self, x_min_range_dunit: float | None, x_max_range_dunit: float | None, y_min_range_dunit: float | None, y_max_range_dunit: float | None
    ) -> None:
        """Set the zoom range limits in data units.

        Args:
            x_min_range_dunit (float | None): Minimum zoom range for x axis in data units. If None, no limit is applied.
            x_max_range_dunit (float | None): Maximum zoom range for x axis in data units. If None, no limit is applied.
            y_min_range_dunit (float | None): Minimum zoom range for y axis in data units. If None, no limit is applied.
            y_max_range_dunit (float | None): Maximum zoom range for y axis in data units. If None, no limit is applied.
        """
        self._zoom_x_min_range_dunit = x_min_range_dunit
        self._zoom_x_max_range_dunit = x_max_range_dunit
        self._zoom_y_min_range_dunit = y_min_range_dunit
        self._zoom_y_max_range_dunit = y_max_range_dunit

    # =============================================================================
    #
    # =============================================================================
    def _on_button_press(self, mouse_event: MouseEvent):
        # Store pixel coordinates instead of data coordinates
        self._button_press_x_ndc = mouse_event.x_ndc
        self._button_press_y_ndc = mouse_event.y_ndc

        self._x_min_dunit, self._x_max_dunit, self._y_min_dunit, self._y_max_dunit = self._axes_display.get_limits_dunit()

    def _on_button_release(self, mouse_event: MouseEvent):
        self._button_press_x_ndc = None
        self._button_press_y_ndc = None
        self._x_min_dunit = None
        self._x_max_dunit = None
        self._y_min_dunit = None
        self._y_max_dunit = None

    def _on_mouse_move(self, mouse_event: MouseEvent):
        # sanity check
        if self._button_press_x_ndc is None or self._button_press_y_ndc is None:
            return
        if self._x_min_dunit is None or self._x_max_dunit is None or self._y_min_dunit is None or self._y_max_dunit is None:
            return

        # Calculate the delta in NDC units
        delta_x_ndc: float = mouse_event.x_ndc - self._button_press_x_ndc
        delta_y_ndc: float = mouse_event.y_ndc - self._button_press_y_ndc

        # Compute new limits in data space for the viewports
        new_x_min_dunit: float = self._x_min_dunit - (delta_x_ndc / 2.0) * (self._x_max_dunit - self._x_min_dunit)
        new_x_max_dunit: float = self._x_max_dunit - (delta_x_ndc / 2.0) * (self._x_max_dunit - self._x_min_dunit)
        new_y_min_dunit: float = self._y_min_dunit - (delta_y_ndc / 2.0) * (self._y_max_dunit - self._y_min_dunit)
        new_y_max_dunit: float = self._y_max_dunit - (delta_y_ndc / 2.0) * (self._y_max_dunit - self._y_min_dunit)

        # =============================================================================
        # Update the axes limits in data unit
        # =============================================================================
        self._set_axes_limits_dunit(new_x_min_dunit, new_x_max_dunit, new_y_min_dunit, new_y_max_dunit)

    def _on_mouse_scroll(self, mouse_event: MouseEvent):
        scale_factor: float = 1 / self._base_scale if mouse_event.scroll_steps >= 0 else self._base_scale

        # Get current limits in data unit
        x_min_dunit, x_max_dunit, y_min_dunit, y_max_dunit = self._axes_display.get_limits_dunit()

        # print(f"scale_factor: {scale_factor}")

        # Calculate mouse position in data units
        mouse_x_dunit: float = x_min_dunit + (mouse_event.x_ndc + 1.0) / 2.0 * (x_max_dunit - x_min_dunit)
        mouse_y_dunit: float = y_min_dunit + (mouse_event.y_ndc + 1.0) / 2.0 * (y_max_dunit - y_min_dunit)

        # Calculate new limits in data units, keeping the mouse position fixed
        new_width_dunit: float = (x_max_dunit - x_min_dunit) * scale_factor
        new_height_dunit: float = (y_max_dunit - y_min_dunit) * scale_factor
        relative_x: float = (x_max_dunit - mouse_x_dunit) / (x_max_dunit - x_min_dunit)
        relative_y: float = (y_max_dunit - mouse_y_dunit) / (y_max_dunit - y_min_dunit)

        # Compute new limits in data units
        new_x_min_dunit: float = mouse_x_dunit - new_width_dunit * (1 - relative_x)
        new_x_max_dunit: float = mouse_x_dunit + new_width_dunit * (relative_x)
        new_y_min_dunit: float = mouse_y_dunit - new_height_dunit * (1 - relative_y)
        new_y_max_dunit: float = mouse_y_dunit + new_height_dunit * (relative_y)

        # =============================================================================
        # Update the axes limits in data unit
        # =============================================================================

        self._set_axes_limits_dunit(new_x_min_dunit, new_x_max_dunit, new_y_min_dunit, new_y_max_dunit)

    # =============================================================================
    #
    # =============================================================================
    def _set_axes_limits_dunit(self, x_min_dunit: float, x_max_dunit: float, y_min_dunit: float, y_max_dunit: float) -> None:
        """Set the axes limits in data units. Applies pan and zoom limits if set.

        Args:
            x_min_dunit (float): Minimum x limit in data units.
            x_max_dunit (float): Maximum x limit in data units.
            y_min_dunit (float): Minimum y limit in data units.
            y_max_dunit (float): Maximum y limit in data units.
        """
        # =============================================================================
        # Enforce min/max zoom range for x/y
        # =============================================================================

        # Enforce minimum zoom range if set for x
        if self._zoom_x_min_range_dunit is not None:
            zoom_x_range_dunit: float = x_max_dunit - x_min_dunit
            if zoom_x_range_dunit < self._zoom_x_min_range_dunit:
                # Clamp the zoom range
                center_x_dunit: float = (x_min_dunit + x_max_dunit) / 2.0
                x_min_dunit = center_x_dunit - self._zoom_x_min_range_dunit / 2.0
                x_max_dunit = center_x_dunit + self._zoom_x_min_range_dunit / 2.0
        # Enforce minimum zoom range if set for y
        if self._zoom_y_min_range_dunit is not None:
            zoom_y_range_dunit: float = y_max_dunit - y_min_dunit
            if zoom_y_range_dunit < self._zoom_y_min_range_dunit:
                # Clamp the zoom range
                center_y_dunit: float = (y_min_dunit + y_max_dunit) / 2.0
                y_min_dunit = center_y_dunit - self._zoom_y_min_range_dunit / 2.0
                y_max_dunit = center_y_dunit + self._zoom_y_min_range_dunit / 2.0
        # Enforce maximum zoom range if set for x
        if self._zoom_x_max_range_dunit is not None:
            zoom_x_range_dunit: float = x_max_dunit - x_min_dunit
            if zoom_x_range_dunit > self._zoom_x_max_range_dunit:
                # Clamp the zoom range
                center_x_dunit: float = (x_min_dunit + x_max_dunit) / 2.0
                x_min_dunit = center_x_dunit - self._zoom_x_max_range_dunit / 2.0
                x_max_dunit = center_x_dunit + self._zoom_x_max_range_dunit / 2.0
        # Enforce maximum zoom range if set for y
        if self._zoom_y_max_range_dunit is not None:
            zoom_y_range_dunit: float = y_max_dunit - y_min_dunit
            if zoom_y_range_dunit > self._zoom_y_max_range_dunit:
                # Clamp the zoom range
                center_y_dunit: float = (y_min_dunit + y_max_dunit) / 2.0
                y_min_dunit = center_y_dunit - self._zoom_y_max_range_dunit / 2.0
                y_max_dunit = center_y_dunit + self._zoom_y_max_range_dunit / 2.0

        # =============================================================================
        # Enforce pan limit
        # =============================================================================
        if self._pan_x_min_dunit is not None:
            if x_min_dunit <= self._pan_x_min_dunit:
                shift_dunit: float = self._pan_x_min_dunit - x_min_dunit
                x_min_dunit += shift_dunit
                x_max_dunit += shift_dunit
        if self._pan_x_max_dunit is not None:
            if x_max_dunit >= self._pan_x_max_dunit:
                shift_dunit: float = x_max_dunit - self._pan_x_max_dunit
                x_min_dunit -= shift_dunit
                x_max_dunit -= shift_dunit
        if self._pan_y_min_dunit is not None:
            if y_min_dunit <= self._pan_y_min_dunit:
                shift_dunit: float = self._pan_y_min_dunit - y_min_dunit
                y_min_dunit += shift_dunit
                y_max_dunit += shift_dunit
        if self._pan_y_max_dunit is not None:
            if y_max_dunit >= self._pan_y_max_dunit:
                shift_dunit: float = y_max_dunit - self._pan_y_max_dunit
                y_min_dunit -= shift_dunit
                y_max_dunit -= shift_dunit

        # handle edge case where pan limits are smaller goes beyond min/max limits by epsilon
        # - sometimes floating point errors can cause this issue e.g. self._pan_x_min_dunit = -2.0 but x_min_dunit = -2.00000001
        epsilon: float = 1e-8
        if self._pan_x_min_dunit is not None:
            if abs(x_min_dunit - self._pan_x_min_dunit) < epsilon:
                x_min_dunit = self._pan_x_min_dunit
        if self._pan_x_max_dunit is not None:
            if abs(x_max_dunit - self._pan_x_max_dunit) < epsilon:
                x_max_dunit = self._pan_x_max_dunit
        if self._pan_y_min_dunit is not None:
            if abs(y_min_dunit - self._pan_y_min_dunit) < epsilon:
                y_min_dunit = self._pan_y_min_dunit
        if self._pan_y_max_dunit is not None:
            if abs(y_max_dunit - self._pan_y_max_dunit) < epsilon:
                y_max_dunit = self._pan_y_max_dunit

        # =============================================================================
        # Finally set the new limits
        # =============================================================================

        # print(f"Set axes limits: x=({x_min_dunit}, {x_max_dunit}), y=({y_min_dunit}, {y_max_dunit})")

        self._axes_display.set_limits_dunit(x_min_dunit, x_max_dunit, y_min_dunit, y_max_dunit)
