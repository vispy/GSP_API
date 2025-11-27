# stdlib imports
from typing import Any
import typing

# pip imports
import matplotlib.backend_bases


# local imports
from gsp.core import Event
from gsp.core import Canvas, Viewport
from gsp.utils.unit_utils import UnitUtils
from gsp_matplotlib.renderer import MatplotlibRenderer
from .viewport_events_types import KeyEvent, MouseEvent, EventType
from .viewport_events_base import ViewportEventsBase
from .viewport_events_types import KeyEvent, MouseEvent, KeyboardEventCallback, MouseEventCallback


class ViewportEventsMatplotlib(ViewportEventsBase):
    """MatplotlibRenderer event handler for viewport"""

    __slots__ = [
        "_renderer",
        "_viewport",
        "_has_key_focus",
        "_mpl_key_press_cid",
        "_mpl_key_release_cid",
        "_mpl_button_press_cid",
        "_mpl_button_release_cid",
        "_mpl_mouse_move_cid",
        "_mpl_scroll_event_cid",
    ]

    def __init__(self, renderer: MatplotlibRenderer, viewport: Viewport) -> None:

        self._renderer = renderer
        """MatplotlibRenderer associated with this event handler"""
        self._viewport = viewport
        """viewport associated with this event handler"""
        self._has_key_focus = False
        """True if this viewport has the keyboard focus"""

        # Intanciate events
        self.key_press_event = Event[KeyboardEventCallback]()
        self.key_release_event = Event[KeyboardEventCallback]()
        self.button_press_event = Event[MouseEventCallback]()
        self.button_release_event = Event[MouseEventCallback]()
        self.mouse_move_event = Event[MouseEventCallback]()
        self.mouse_scroll_event = Event[MouseEventCallback]()

        # event connections
        mpl_canvas: matplotlib.backend_bases.FigureCanvasBase = self._renderer.get_mpl_figure().canvas
        self._mpl_key_press_cid = mpl_canvas.mpl_connect("key_press_event", typing.cast(Any, self._on_key_press))
        self._mpl_key_release_cid = mpl_canvas.mpl_connect("key_release_event", typing.cast(Any, self._on_key_release))
        self._mpl_button_press_cid = mpl_canvas.mpl_connect("button_press_event", typing.cast(Any, self._on_button_press))
        self._mpl_button_release_cid = mpl_canvas.mpl_connect("button_release_event", typing.cast(Any, self._on_button_release))
        self._mpl_mouse_move_cid = mpl_canvas.mpl_connect("motion_notify_event", typing.cast(Any, self._on_mouse_move))
        self._mpl_scroll_event_cid = mpl_canvas.mpl_connect("scroll_event", typing.cast(Any, self._on_mouse_scroll))

    def close(self):
        mpl_canvas: matplotlib.backend_bases.FigureCanvasBase = self._renderer.get_mpl_figure().canvas
        if self._mpl_key_press_cid is not None:
            mpl_canvas.mpl_disconnect(self._mpl_key_press_cid)
            self._mpl_key_press_cid = None
        if self._mpl_key_release_cid is not None:
            mpl_canvas.mpl_disconnect(self._mpl_key_release_cid)
            self._mpl_key_release_cid = None
        if self._mpl_button_press_cid is not None:
            mpl_canvas.mpl_disconnect(self._mpl_button_press_cid)
            self._mpl_button_press_cid = None
        if self._mpl_button_release_cid is not None:
            mpl_canvas.mpl_disconnect(self._mpl_button_release_cid)
            self._mpl_button_release_cid = None
        if self._mpl_mouse_move_cid is not None:
            mpl_canvas.mpl_disconnect(self._mpl_mouse_move_cid)
            self._mpl_mouse_move_cid = None
        if self._mpl_scroll_event_cid is not None:
            mpl_canvas.mpl_disconnect(self._mpl_scroll_event_cid)
            self._mpl_scroll_event_cid = None

    # =============================================================================
    # Matplotlib event handler
    # =============================================================================

    def _on_key_press(self, mpl_key_event: matplotlib.backend_bases.KeyEvent) -> None:
        # discard events outside the viewport
        if self._has_key_focus is False:
            return
        # convert and dispatch event
        keyboard_event = self._mpl_key_event_to_gsp(mpl_key_event, EventType.KEY_PRESS)
        self.key_press_event.dispatch(keyboard_event)

    def _on_key_release(self, mpl_key_event: matplotlib.backend_bases.KeyEvent) -> None:
        # discard events outside the viewport
        if self._has_key_focus is False:
            return
        # convert and dispatch event
        keyboard_event = self._mpl_key_event_to_gsp(mpl_key_event, EventType.KEY_RELEASE)
        self.key_release_event.dispatch(keyboard_event)

    def _on_button_press(self, mpl_mouse_event: matplotlib.backend_bases.MouseEvent) -> None:
        # print("matplotlib button press event:", mpl_mouse_event)
        # Set key focus if the event is inside the viewport, otherwise remove key focus
        if self._viewport_contains_mpl_mouse_event(mpl_mouse_event):
            self._has_key_focus = True
        else:
            self._has_key_focus = False

        # discard events outside the viewport
        if self._viewport_contains_mpl_mouse_event(mpl_mouse_event) is False:
            return

        # convert and dispatch event
        mouse_event = self._mpl_mouse_event_to_gsp(mpl_mouse_event, EventType.BUTTON_PRESS)
        self.button_press_event.dispatch(mouse_event)

    def _on_button_release(self, mpl_mouse_event: matplotlib.backend_bases.MouseEvent) -> None:
        # print("matplotlib button release event:", mpl_mouse_event)

        # discard events outside the viewport
        if self._viewport_contains_mpl_mouse_event(mpl_mouse_event) is False:
            return
        # convert and dispatch event
        mouse_event = self._mpl_mouse_event_to_gsp(mpl_mouse_event, EventType.BUTTON_RELEASE)
        self.button_release_event.dispatch(mouse_event)

    def _on_mouse_move(self, mpl_mouse_event: matplotlib.backend_bases.MouseEvent) -> None:
        # discard events outside the viewport
        if self._viewport_contains_mpl_mouse_event(mpl_mouse_event) is False:
            return
        # convert and dispatch event
        mouse_event = self._mpl_mouse_event_to_gsp(mpl_mouse_event, EventType.MOUSE_MOVE)
        self.mouse_move_event.dispatch(mouse_event)

    def _on_mouse_scroll(self, mpl_mouse_event: matplotlib.backend_bases.MouseEvent) -> None:
        # discard events outside the viewport
        if self._viewport_contains_mpl_mouse_event(mpl_mouse_event) is False:
            return
        # convert and dispatch event
        mouse_event = self._mpl_mouse_event_to_gsp(mpl_mouse_event, EventType.MOUSE_SCROLL)
        self.mouse_scroll_event.dispatch(mouse_event)

    # =============================================================================
    #
    # =============================================================================

    def _viewport_contains_mpl_mouse_event(self, mpl_mouse_event: matplotlib.backend_bases.MouseEvent) -> bool:
        """Check if the matplotlib mouse event is inside this viewport"""
        mouse_x = mpl_mouse_event.x / UnitUtils.device_pixel_ratio()
        mouse_y = mpl_mouse_event.y / UnitUtils.device_pixel_ratio()
        if mouse_x < self._viewport.get_x():
            return False
        if mouse_x >= self._viewport.get_x() + self._viewport.get_width():
            return False
        if mouse_y < self._viewport.get_y():
            return False
        if mouse_y >= self._viewport.get_y() + self._viewport.get_height():
            return False
        return True

    # =============================================================================
    # Conversion matplotlib event to gsp events
    # =============================================================================
    def _mpl_mouse_event_to_gsp(self, mpl_mouse_event: matplotlib.backend_bases.MouseEvent, event_type: EventType) -> MouseEvent:
        # Sanity check
        assert self._viewport_contains_mpl_mouse_event(mpl_mouse_event), "Mouse event is outside the viewport"

        mouse_x = mpl_mouse_event.x / UnitUtils.device_pixel_ratio()
        mouse_y = mpl_mouse_event.y / UnitUtils.device_pixel_ratio()
        x_viewport = mouse_x - self._viewport.get_x()
        y_viewport = mouse_y - self._viewport.get_y()
        mouse_event = MouseEvent(
            viewport_uuid=self._viewport.get_uuid(),
            event_type=event_type,
            x=(x_viewport / self._viewport.get_width() - 0.5) * 2.0,
            y=(y_viewport / self._viewport.get_height() - 0.5) * 2.0,
            left_button=mpl_mouse_event.button == 1,
            middle_button=mpl_mouse_event.button == 2,
            right_button=mpl_mouse_event.button == 3,
            scroll_steps=mpl_mouse_event.step if hasattr(mpl_mouse_event, "step") else 0.0,
        )
        return mouse_event

    def _mpl_key_event_to_gsp(self, mpl_key_event: matplotlib.backend_bases.KeyEvent, event_type: EventType) -> KeyEvent:
        assert mpl_key_event.key is not None
        keyboard_event = KeyEvent(
            viewport_uuid=self._viewport.get_uuid(),
            event_type=event_type,
            key_name=mpl_key_event.key,
        )
        return keyboard_event
