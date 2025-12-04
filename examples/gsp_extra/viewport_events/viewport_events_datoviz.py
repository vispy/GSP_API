# pip imports
import datoviz as dvz
from datoviz._figure import Figure as _DvzFigure


# local imports
from gsp.core import Event
from gsp.core import Viewport
from gsp_datoviz.renderer import DatovizRenderer
from .viewport_events_base import ViewportEventsBase
from .viewport_events_types import EventType
from .viewport_events_types import KeyEvent, MouseEvent, CanvasResizeEvent
from .viewport_events_types import KeyboardEventCallback, MouseEventCallback, CanvasResizeEventCallback


class ViewportEventsDatoviz(ViewportEventsBase):
    """DatovizRenderer event handler for viewport"""

    __slots__ = ("_renderer", "_viewport", "_has_key_focus", "_is_closed")

    def __init__(self, renderer: DatovizRenderer, viewport: Viewport) -> None:

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
            dvz_event_name = dvz_mouse_event.mouse_event()
            dvz_mouse_pos = dvz_mouse_event.pos()
            dvz_button_name = dvz_mouse_event.button_name()
            dvz_wheel = dvz_mouse_event.wheel()

            # Convert fields to our MouseEvent
            if dvz_event_name == "press":
                event_type = EventType.BUTTON_PRESS
            elif dvz_event_name == "release":
                event_type = EventType.BUTTON_RELEASE
            elif dvz_event_name == "move":
                event_type = EventType.MOUSE_MOVE
            elif dvz_event_name == "wheel":
                event_type = EventType.MOUSE_SCROLL
            else:
                print(f'"Unknown dvz mouse event name: {dvz_event_name}"')
                return  # Unknown event

            event_x: float = dvz_mouse_pos[0]
            event_y: float = dvz_mouse_pos[1]

            left_button: bool = dvz_button_name == "left"
            middle_button: bool = dvz_button_name == "middle"
            right_button: bool = dvz_button_name == "right"

            event_scroll_steps: float = dvz_wheel if dvz_wheel is not None else 0.0

            # Create our MouseEvent
            mouse_event = MouseEvent(
                viewport_uuid=self._viewport.get_uuid(),
                event_type=event_type,
                x=event_x,
                y=event_y,
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
        """Close the event handler and release resources"""

        # no more dispatch events (datoviz doesnt allow to disconnect events)
        self._is_closed = True

    # =============================================================================
    #
    # =============================================================================

    def _viewport_contains_dvz_mouse_event(self, dvz_mouse_event: dvz.MouseEvent) -> bool:
        """Check if the matplotlib mouse event is inside this viewport"""

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
