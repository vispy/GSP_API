"""Class AxesPanZoom to handle panning and zooming in a viewport."""

# local imports
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
        """Base scale for zooming."""
        self._axes_display = axes_display
        """Axes display to update."""

        self._button_press_x_ndc: float | None = None
        """X coordinate of the button press in NDC units."""
        self._button_press_y_ndc: float | None = None
        """Y coordinate of the button press in NDC units."""

        self._x_min_dunit: float | None = None
        """Current x minimum viewport in data units."""
        self._x_max_dunit: float | None = None
        """Current x maximum viewport in data units."""
        self._y_min_dunit: float | None = None
        """Current y minimum viewport in data units."""
        self._y_max_dunit: float | None = None
        """Current y maximum viewport in data units."""

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

    def _on_button_move(self, mouse_event: MouseEvent):
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

        # Update the axes limits in data space
        self._axes_display.set_limits_dunit(new_x_min_dunit, new_x_max_dunit, new_y_min_dunit, new_y_max_dunit)

    def _on_mouse_scroll(self, mouse_event: MouseEvent):
        scale_factor: float = 1 / self._base_scale if mouse_event.scroll_steps >= 0 else self._base_scale

        x_min_dunit, x_max_dunit, y_min_dunit, y_max_dunit = self._axes_display.get_limits_dunit()

        # print(f"scale_factor: {scale_factor}")

        mouse_x_dunit: float = x_min_dunit + (mouse_event.x_ndc + 1.0) / 2.0 * (x_max_dunit - x_min_dunit)
        mouse_y_dunit: float = y_min_dunit + (mouse_event.y_ndc + 1.0) / 2.0 * (y_max_dunit - y_min_dunit)

        new_width: float = (x_max_dunit - x_min_dunit) * scale_factor
        new_height: float = (y_max_dunit - y_min_dunit) * scale_factor
        relative_x: float = (x_max_dunit - mouse_x_dunit) / (x_max_dunit - x_min_dunit)
        relative_y: float = (y_max_dunit - mouse_y_dunit) / (y_max_dunit - y_min_dunit)

        new_x_min: float = mouse_x_dunit - new_width * (1 - relative_x)
        new_x_max: float = mouse_x_dunit + new_width * (relative_x)
        new_y_min: float = mouse_y_dunit - new_height * (1 - relative_y)
        new_y_max: float = mouse_y_dunit + new_height * (relative_y)

        self._axes_display.set_limits_dunit(new_x_min, new_x_max, new_y_min, new_y_max)

        # print(f"New limits: x[{new_x_min}, {new_x_max}] y[{new_y_min}, {new_y_max}]")
