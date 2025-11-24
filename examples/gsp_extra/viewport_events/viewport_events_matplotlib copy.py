# stdlib imports
from typing import Any
import typing

# pip imports
import matplotlib.backend_bases


# local imports
from gsp.core import Event
from gsp.core import Canvas, Viewport
from gsp_matplotlib.renderer import MatplotlibRenderer
from .viewport_events_types import KeyEvent, MouseEvent, EventType
from .viewport_event_base import ViewportEventBase
from .viewport_events_types import KeyEvent, MouseEvent, KeyboardEventCallback, MouseEventCallback


class ViewportEventsMatplotlib(ViewportEventBase):
    """MatplotlibRenderer event handler for viewport"""

    __slots__ = (
        "_renderer",
        "_viewport",
        "_mpl_axes",
        "_mpl_figure",
        "_mpl_key_press_cid",
        "_mpl_key_release_cid",
        "_mpl_button_press_cid",
        "_mpl_button_release_cid",
    )

    def __init__(self, renderer: MatplotlibRenderer, viewport: Viewport) -> None:

        self._renderer = renderer
        self._viewport = viewport

        self._mpl_axes = renderer._axes[self._viewport.get_uuid()]
        self._mpl_figure = self._mpl_axes.figure
        self._focused_axes = self._mpl_axes

        # Intanciate events
        self.key_press_event = Event[KeyboardEventCallback]()
        self.key_release_event = Event[KeyboardEventCallback]()
        self.button_press_event = Event[MouseEventCallback]()
        self.button_release_event = Event[MouseEventCallback]()
        self.mouse_move_event = Event[MouseEventCallback]()

        # event connections
        mpl_canvas: matplotlib.backend_bases.FigureCanvasBase = self._mpl_figure.canvas
        self._mpl_key_press_cid = mpl_canvas.mpl_connect("key_press_event", typing.cast(Any, self._on_key_press))
        self._mpl_key_release_cid = mpl_canvas.mpl_connect("key_release_event", typing.cast(Any, self._on_key_release))
        self._mpl_button_press_cid = mpl_canvas.mpl_connect("button_press_event", typing.cast(Any, self._on_button_press))
        self._mpl_button_release_cid = mpl_canvas.mpl_connect("button_release_event", typing.cast(Any, self._on_button_release))
        self._mpl_mouse_move_cid = mpl_canvas.mpl_connect("motion_notify_event", typing.cast(Any, self._on_mouse_move))

    def close(self):
        mpl_canvas: matplotlib.backend_bases.FigureCanvasBase = self._mpl_figure.canvas
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

    # =============================================================================
    # Matplotlib event handler
    # =============================================================================
    def _on_key_press(self, mpl_key_event: matplotlib.backend_bases.KeyEvent) -> None:
        # discard events outside the viewport
        if self._focused_axes is not self._mpl_axes:
            return
        # convert and dispatch event
        keyboard_event = self._mpl_key_event_to_gsp(mpl_key_event, EventType.KEY_PRESS)
        self.key_press_event.dispatch(keyboard_event)

    def _on_key_release(self, mpl_key_event: matplotlib.backend_bases.KeyEvent) -> None:
        # discard events outside the viewport
        if self._focused_axes is not self._mpl_axes:
            return
        # convert and dispatch event
        keyboard_event = self._mpl_key_event_to_gsp(mpl_key_event, EventType.KEY_RELEASE)
        self.key_release_event.dispatch(keyboard_event)

    def _on_button_press(self, mpl_mouse_event: matplotlib.backend_bases.MouseEvent) -> None:
        # Handle focus change
        if mpl_mouse_event.inaxes is not None:
            self._focused_axes = mpl_mouse_event.inaxes
            # print("Focus set to:", self._focused_axes)

        # discard events outside the viewport
        if self._is_mouse_event_not_in_viewport(mpl_mouse_event):
            return
        # convert and dispatch event
        mouse_event = self._mpl_mouse_event_to_gsp(mpl_mouse_event, EventType.BUTTON_PRESS)
        self.button_press_event.dispatch(mouse_event)

    def _on_button_release(self, mpl_mouse_event: matplotlib.backend_bases.MouseEvent) -> None:
        # discard events outside the viewport
        if self._is_mouse_event_not_in_viewport(mpl_mouse_event):
            return
        # convert and dispatch event
        mouse_event = self._mpl_mouse_event_to_gsp(mpl_mouse_event, EventType.BUTTON_RELEASE)
        self.button_release_event.dispatch(mouse_event)

    def _on_mouse_move(self, mpl_mouse_event: matplotlib.backend_bases.MouseEvent) -> None:
        # discard events outside the viewport
        if self._is_mouse_event_not_in_viewport(mpl_mouse_event):
            return
        # convert and dispatch event
        mouse_event = self._mpl_mouse_event_to_gsp(mpl_mouse_event, EventType.MOUSE_MOVE)
        self.mouse_move_event.dispatch(mouse_event)

    # =============================================================================
    #
    # =============================================================================

    def _is_mouse_event_not_in_viewport(self, mpl_mouse_event: matplotlib.backend_bases.MouseEvent) -> bool:
        """Check if the matplotlib mouse event is inside the axes of this viewport"""
        if mpl_mouse_event.inaxes is None:
            return True
        not_in_viewport = mpl_mouse_event.inaxes is not self._mpl_axes
        return not_in_viewport

    # =============================================================================
    # Conversion matplotlib event to gsp events
    # =============================================================================
    def _mpl_mouse_event_to_gsp(self, mpl_mouse_event: matplotlib.backend_bases.MouseEvent, event_type: EventType) -> MouseEvent:
        axes_width = typing.cast(float, self._mpl_axes.bbox.width)
        axes_height = typing.cast(float, self._mpl_axes.bbox.height)
        mouse_event = MouseEvent(
            viewport_uuid=self._viewport.get_uuid(),
            event_type=event_type,
            x=(mpl_mouse_event.x / axes_width - 0.5) * 2.0,
            y=(mpl_mouse_event.y / axes_height - 0.5) * 2.0,
            left_button=mpl_mouse_event.button == 1,
            middle_button=mpl_mouse_event.button == 2,
            right_button=mpl_mouse_event.button == 3,
            scroll_steps=mpl_mouse_event.step if hasattr(mpl_mouse_event, "step") else 0.0,
        )
        # print(mouse_event)
        return mouse_event

    def _mpl_key_event_to_gsp(self, mpl_key_event: matplotlib.backend_bases.KeyEvent, event_type: EventType) -> KeyEvent:
        assert mpl_key_event.key is not None
        keyboard_event = KeyEvent(
            viewport_uuid=self._viewport.get_uuid(),
            event_type=event_type,
            key_name=mpl_key_event.key,
        )
        # function_name = typing.cast(FrameType, inspect.currentframe()).f_code.co_name
        # print(f"{self.__class__.__name__}.{function_name}: {keyboard_event}")
        return keyboard_event
