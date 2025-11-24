# stdlib imports
from abc import ABC, abstractmethod

# local imports
from gsp.core import Event
from .viewport_events_types import KeyEvent, MouseEvent, KeyboardEventCallback, MouseEventCallback


class ViewportEventsBase(ABC):
    """Base class for window event handlers for camera controls"""

    __slots__ = [
        # Define events
        "key_press_event",
        "key_release_event",
        "button_press_event",
        "button_release_event",
        "mouse_move_event",
    ]

    key_press_event: Event[KeyboardEventCallback]
    key_release_event: Event[KeyboardEventCallback]
    button_press_event: Event[MouseEventCallback]
    button_release_event: Event[MouseEventCallback]
    mouse_move_event: Event[MouseEventCallback]
