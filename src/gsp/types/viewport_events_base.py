"""Base class for viewport event handlers."""

# stdlib imports
from abc import ABC, abstractmethod

# local imports
from gsp.core import Event
from .viewport_events_types import KeyboardEventCallback, MouseEventCallback, CanvasResizeEventCallback


class ViewportEventsBase(ABC):
    """Base class for window event handlers for camera controls."""

    __slots__ = [
        "key_press_event",
        "key_release_event",
        "button_press_event",
        "button_release_event",
        "mouse_move_event",
        "mouse_scroll_event",
        "canvas_resize_event",
    ]

    key_press_event: Event[KeyboardEventCallback]
    """Event triggered on key press"""
    key_release_event: Event[KeyboardEventCallback]
    """Event triggered on key release"""
    button_press_event: Event[MouseEventCallback]
    """Event triggered on mouse button press"""
    button_release_event: Event[MouseEventCallback]
    """Event triggered on mouse button release"""
    mouse_move_event: Event[MouseEventCallback]
    """Event triggered on mouse move"""
    mouse_scroll_event: Event[MouseEventCallback]
    """Event triggered on mouse scroll"""
    mouse_scroll_event: Event[MouseEventCallback]
    """Event triggered on mouse scroll"""
    canvas_resize_event: Event[CanvasResizeEventCallback]
    """Event triggered on canvas resize"""
