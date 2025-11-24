# stdlib imports
from types import FrameType
from typing import Any
import typing
import inspect

# pip imports
import matplotlib.figure
import matplotlib.backend_bases


# local imports
from .viewport_events_types import KeyboardEvent, MouseEvent, EventType
from .viewport_event_base import ViewportEventBase


class ViewportEventsMatplotlib(ViewportEventBase):
    """Matplotlib window event handler for camera controls"""

    __slots__ = ("_figure", "_mpl_key_press_cid", "_mpl_key_release_cid", "_mpl_button_press_cid", "_mpl_button_release_cid")

    def __init__(self, mpl_figure: matplotlib.figure.Figure):
        self._figure = mpl_figure

        # event connections
        mpl_canvas: matplotlib.backend_bases.FigureCanvasBase = self._figure.canvas
        self._mpl_key_press_cid = mpl_canvas.mpl_connect("key_press_event", typing.cast(Any, self._on_key_press))
        self._mpl_key_release_cid = mpl_canvas.mpl_connect("key_release_event", typing.cast(Any, self._on_key_release))
        self._mpl_button_press_cid = mpl_canvas.mpl_connect("button_press_event", typing.cast(Any, self._on_button_press))
        self._mpl_button_release_cid = mpl_canvas.mpl_connect("button_release_event", typing.cast(Any, self._on_button_release))
        self._mpl_mouse_move_cid = mpl_canvas.mpl_connect("motion_notify_event", typing.cast(Any, self._on_mouse_move))

    def close(self):
        mpl_canvas: matplotlib.backend_bases.FigureCanvasBase = self._figure.canvas
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
    def _on_key_press(self, mpl_event: matplotlib.backend_bases.KeyEvent) -> None:
        keyboardEvent = self._mpl_key_event_to_gsp(mpl_event, EventType.KEY_PRESS)
        self.key_press_event.dispatch(keyboardEvent)

    def _on_key_release(self, mpl_event: matplotlib.backend_bases.KeyEvent) -> None:
        keyboardEvent = self._mpl_key_event_to_gsp(mpl_event, EventType.KEY_RELEASE)
        self.key_release_event.dispatch(keyboardEvent)

    def _on_button_press(self, mpl_mouse_event: matplotlib.backend_bases.MouseEvent) -> None:
        mouseEvent = self._mpl_mouse_event_to_gsp(mpl_mouse_event, EventType.BUTTON_PRESS)
        self.button_press_event.dispatch(mouseEvent)

    def _on_button_release(self, mpl_mouse_event: matplotlib.backend_bases.MouseEvent) -> None:
        mouseEvent = self._mpl_mouse_event_to_gsp(mpl_mouse_event, EventType.BUTTON_RELEASE)
        self.button_release_event.dispatch(mouseEvent)

    def _on_mouse_move(self, mpl_mouse_event: matplotlib.backend_bases.MouseEvent) -> None:
        mouseEvent = self._mpl_mouse_event_to_gsp(mpl_mouse_event, EventType.MOUSE_MOVE)
        self.mouse_move_event.dispatch(mouseEvent)

    # =============================================================================
    # Conversion matplotlib event to gsp events
    # =============================================================================
    def _mpl_mouse_event_to_gsp(self, mpl_mouse_event: matplotlib.backend_bases.MouseEvent, event_type: EventType) -> MouseEvent:
        mpl_canvas: matplotlib.backend_bases.FigureCanvasBase = self._figure.canvas
        canvas_width, canvas_height = mpl_canvas.get_width_height()
        mouse_event = MouseEvent(
            event_type=event_type,
            x=(mpl_mouse_event.x / canvas_width - 0.5) * 2.0,
            y=(mpl_mouse_event.y / canvas_height - 0.5) * 2.0,
            left_button=mpl_mouse_event.button == 1,
            middle_button=mpl_mouse_event.button == 2,
            right_button=mpl_mouse_event.button == 3,
            scroll_steps=mpl_mouse_event.step if hasattr(mpl_mouse_event, "step") else 0.0,
        )
        # print(mouse_event)
        return mouse_event

    def _mpl_key_event_to_gsp(self, mpl_key_event: matplotlib.backend_bases.KeyEvent, event_type: EventType) -> KeyboardEvent:
        assert mpl_key_event.key is not None
        keyboard_event = KeyboardEvent(
            event_type=event_type,
            key_name=mpl_key_event.key,
        )
        # function_name = typing.cast(FrameType, inspect.currentframe()).f_code.co_name
        # print(f"{self.__class__.__name__}.{function_name}: {keyboard_event}")
        return keyboard_event
