"""DatovizRenderer event handler for viewport events."""

# pip imports
import datoviz as dvz
from datoviz._figure import Figure as _DvzFigure


# local imports
from gsp.core import Event
from gsp.core import Viewport
from gsp_datoviz.renderer import DatovizRenderer
from gsp.types.viewport_events_base import ViewportEventsBase
from gsp.types.viewport_events_types import EventType
from gsp.types.viewport_events_types import KeyEvent, MouseEvent, CanvasResizeEvent
from gsp.types.viewport_events_types import KeyboardEventCallback, MouseEventCallback, CanvasResizeEventCallback


class ViewportEventsDatoviz(ViewportEventsBase):
    """DatovizRenderer event handler for viewport."""

    __slots__ = ("_renderer", "_viewport", "_has_key_focus", "_is_closed")

    def __init__(self, renderer: DatovizRenderer, viewport: Viewport) -> None:
        """Initialize the Datoviz viewport event handler."""
        self._renderer = renderer
        """MatplotlibRenderer associated with this event handler"""
        self._viewport = viewport
        """viewport associated with this event handler"""
        self._has_key_focus = False
        """True if this viewport has the keyboard focus"""
        self._is_closed = False
        """True if the event handler is closed"""

        # Intanciate events
        self.key_press_event = Event[KeyboardEventCallback]()
        self.key_release_event = Event[KeyboardEventCallback]()
        self.button_press_event = Event[MouseEventCallback]()
        self.button_release_event = Event[MouseEventCallback]()
        self.mouse_move_event = Event[MouseEventCallback]()
        self.mouse_scroll_event = Event[MouseEventCallback]()
        self.canvas_resize_event = Event[CanvasResizeEventCallback]()

        dvz_app: dvz.App = self._renderer.get_dvz_app()
        dvz_figure: _DvzFigure = self._renderer.get_dvz_figure()

        # =============================================================================
        # Connect keyboard in dvz_app
        # =============================================================================
        @dvz_app.connect(dvz_figure)
        def on_keyboard(dvz_keyboard_event: dvz.KeyboardEvent):
            # if this viewport is closed, ignore events (datoviz doesnt allow to disconnect events)
            if self._is_closed:
                return

            # Read dvz_keyboard_event properties
            dvz_event_name = dvz_keyboard_event.key_event()
            dvz_key_name = dvz_keyboard_event.key_name()

            # Convert fields to our MouseEvent
            if dvz_event_name == "press":
                event_type = EventType.KEY_PRESS
            elif dvz_event_name == "release":
                event_type = EventType.KEY_RELEASE
            else:
                return  # Unknown event

            key_name = dvz_key_name

            # Create our KeyEvent
            key_event = KeyEvent(
                viewport_uuid=self._viewport.get_uuid(),
                event_type=event_type,
                key_name=key_name,
            )

            # dispatch key_event to the proper handler
            if key_event.event_type == EventType.KEY_PRESS:
                self.key_press_event.dispatch(key_event)
            elif key_event.event_type == EventType.KEY_RELEASE:
                self.key_release_event.dispatch(key_event)
            else:
                raise ValueError(f"Unknown key event type: {key_event.event_type}")

        # =============================================================================
        # Connect mouse in dvz_app
        # =============================================================================
        @dvz_app.connect(dvz_figure)
        def on_mouse(dvz_mouse_event: dvz.MouseEvent):
            # if this viewport is closed, ignore events (datoviz doesnt allow to disconnect events)
            if self._is_closed:
                return

            # Set key focus to true if there is a mouse press is inside the viewport, otherwise remove key focus if mouse press is outside
            if dvz_mouse_event.mouse_event() == "press":
                if self._viewport_contains_dvz_mouse_event(dvz_mouse_event):
                    self._has_key_focus = True
                else:
                    self._has_key_focus = False

            # discard events outside the viewport
            if self._viewport_contains_dvz_mouse_event(dvz_mouse_event) is False:
                return

            # Read dvz_mouse_event properties
            dvz_event_name: str = dvz_mouse_event.mouse_event()
            dvz_mouse_pos: tuple[float, float] = dvz_mouse_event.pos()
            dvz_mouse_x_px: float = dvz_mouse_pos[0]
            dvz_mouse_y_px: float = self._renderer.get_canvas().get_height() - dvz_mouse_pos[1]
            dvz_button_name: str = dvz_mouse_event.button_name()
            dvz_wheel: float | None = dvz_mouse_event.wheel()

            # Convert fields to our MouseEvent
            if dvz_event_name == "press":
                print(f"event {dvz_event_name}")
                event_type = EventType.BUTTON_PRESS
            elif dvz_event_name == "release":
                print(f"event {dvz_event_name}")
                event_type = EventType.BUTTON_RELEASE
            elif dvz_event_name == "move":
                event_type = EventType.MOUSE_MOVE
            elif dvz_event_name == "wheel":
                event_type = EventType.MOUSE_SCROLL
            # elif dvz_event_name == "drag_start":
            #     event_type = EventType.BUTTON_PRESS
            # elif dvz_event_name == "drag_stop":
            #     event_type = EventType.BUTTON_RELEASE
            # elif dvz_event_name == "click":
            #     event_type = EventType.BUTTON_PRESS
            else:
                print(f'"Unknown dvz mouse event name: {dvz_event_name}"')
                return  # Unknown event

            event_x: float = (dvz_mouse_x_px - self._viewport.get_x()) / self._viewport.get_width() * 2.0 - 1.0
            event_y: float = (dvz_mouse_y_px - self._viewport.get_y()) / self._viewport.get_height() * 2.0 - 1.0

            # print(f"event_x: {event_x}, event_y: {event_y}")
            # print(
            #     f"dvz_mouse_x_px: {dvz_mouse_x_px}, dvz_mouse_y_px: {dvz_mouse_y_px}viewport x:{self._viewport.get_x()}, y:{self._viewport.get_y()}, w:{self._viewport.get_width()}, h:{self._viewport.get_height()}"
            # )

            left_button: bool = dvz_button_name == "left"
            middle_button: bool = dvz_button_name == "middle"
            right_button: bool = dvz_button_name == "right"

            event_scroll_steps: float = dvz_wheel if dvz_wheel is not None else 0.0

            # Create our MouseEvent
            mouse_event = MouseEvent(
                viewport_uuid=self._viewport.get_uuid(),
                event_type=event_type,
                x_ndc=event_x,
                y_ndc=event_y,
                left_button=left_button,
                middle_button=middle_button,
                right_button=right_button,
                scroll_steps=event_scroll_steps,
            )

            # dispatch mouse_event to the proper handler
            if mouse_event.event_type == EventType.BUTTON_PRESS:
                self.button_press_event.dispatch(mouse_event)
            elif mouse_event.event_type == EventType.BUTTON_RELEASE:
                self.button_release_event.dispatch(mouse_event)
            elif mouse_event.event_type == EventType.MOUSE_MOVE:
                self.mouse_move_event.dispatch(mouse_event)
            elif mouse_event.event_type == EventType.MOUSE_SCROLL:
                self.mouse_scroll_event.dispatch(mouse_event)
            else:
                raise ValueError(f"Unknown mouse event type: {mouse_event.event_type}")

        # =============================================================================
        # Connect resize in dvz_app
        # =============================================================================
        @dvz_app.connect(dvz_figure)
        def on_resize(dvz_resize_event: dvz.WindowEvent):
            canvas_width_px = dvz_resize_event.screen_width()  # TODO may be a good idea to rename .screen_width() to .canvas_width() or similar in datoviz
            canvas_height_px = dvz_resize_event.screen_height()
            # dispatch canvas resize event
            canvas_resize_event = CanvasResizeEvent(
                viewport_uuid=self._viewport.get_uuid(),
                event_type=EventType.CANVAS_RESIZE,
                canvas_width_px=canvas_width_px,
                canvas_height_px=canvas_height_px,
            )
            self.canvas_resize_event.dispatch(canvas_resize_event)

    def close(self):
        """Close the event handler and release resources."""
        # no more dispatch events (datoviz doesnt allow to disconnect events)
        self._is_closed = True

    # =============================================================================
    #
    # =============================================================================

    def _viewport_contains_dvz_mouse_event(self, dvz_mouse_event: dvz.MouseEvent) -> bool:
        """Check if the matplotlib mouse event is inside this viewport.

        Args:
            dvz_mouse_event: Datoviz mouse event.

        Returns:
            True if the mouse event is inside this viewport, False otherwise.
        """
        dvz_mouse_pos = dvz_mouse_event.pos()
        dvz_mouse_x = dvz_mouse_pos[0]
        dvz_mouse_y = self._renderer.get_canvas().get_height() - dvz_mouse_pos[1]

        # print(f"dvz_mouse_x: {dvz_mouse_x}, dvz_mouse_y: {dvz_mouse_y}")

        mouse_x = dvz_mouse_x
        mouse_y = dvz_mouse_y
        if mouse_x < self._viewport.get_x():
            return False
        if mouse_x >= self._viewport.get_x() + self._viewport.get_width():
            return False
        if mouse_y < self._viewport.get_y():
            return False
        if mouse_y >= self._viewport.get_y() + self._viewport.get_height():
            return False
        return True
