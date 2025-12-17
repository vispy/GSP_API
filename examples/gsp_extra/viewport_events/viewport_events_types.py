"""Viewport Event Types and Callback Protocols."""

# stdlib imports
from typing import Protocol
from dataclasses import dataclass
from enum import StrEnum


class EventType(StrEnum):
    """Enumeration of viewport event types.
    
    Defines the different types of user interaction events that can occur
    in a viewport, including keyboard, mouse, and canvas events.
    """
    
    KEY_PRESS = "key_press"
    KEY_RELEASE = "key_release"
    BUTTON_PRESS = "button_press"
    BUTTON_RELEASE = "button_release"
    MOUSE_MOVE = "mouse_move"
    MOUSE_SCROLL = "mouse_scroll"
    CANVAS_RESIZE = "canvas_resize"


@dataclass
class KeyEvent:
    """Represents a keyboard event in a viewport.
    
    Attributes:
        viewport_uuid: The unique identifier of the viewport where the event occurred.
        event_type: The type of keyboard event (KEY_PRESS or KEY_RELEASE).
        key_name: The name of the key that was pressed or released.
    """
    
    viewport_uuid: str
    event_type: EventType
    key_name: str


@dataclass
class MouseEvent:
    """Represents a mouse event in a viewport.
    
    Attributes:
        viewport_uuid: The unique identifier of the viewport where the event occurred.
        event_type: The type of mouse event (BUTTON_PRESS, BUTTON_RELEASE, MOUSE_MOVE, or MOUSE_SCROLL).
        x: The x-coordinate of the mouse position in the viewport.
        y: The y-coordinate of the mouse position in the viewport.
        left_button: Whether the left mouse button is pressed.
        middle_button: Whether the middle mouse button is pressed.
        right_button: Whether the right mouse button is pressed.
        scroll_steps: The number of scroll steps (positive for up, negative for down).
    """
    
    viewport_uuid: str
    event_type: EventType
    x: float
    y: float
    left_button: bool = False
    middle_button: bool = False
    right_button: bool = False
    scroll_steps: float = 0.0


@dataclass
class CanvasResizeEvent:
    """Represents a canvas resize event.
    
    Attributes:
        viewport_uuid: The unique identifier of the viewport affected by the resize.
        event_type: The type of event (CANVAS_RESIZE).
        canvas_width_px: The new width of the canvas in pixels.
        canvas_height_px: The new height of the canvas in pixels.
    """
    
    viewport_uuid: str
    event_type: EventType
    canvas_width_px: int
    canvas_height_px: int


# We can define the expected function signature using a Protocol for clarity.
class KeyboardEventCallback(Protocol):
    """Protocol for keyboard event callback functions.
    
    Defines the signature for functions that handle keyboard events.
    """
    
    def __call__(self, key_event: KeyEvent) -> None:
        """Handle a keyboard event."""


class MouseEventCallback(Protocol):
    """Protocol for mouse event callback functions.
    
    Defines the signature for functions that handle mouse events.
    """
    
    def __call__(self, mouse_event: MouseEvent) -> None: 
        """Handle a mouse event."""
        ...


class CanvasResizeEventCallback(Protocol):
    """Protocol for canvas resize event callback functions.
    
    Defines the signature for functions that handle canvas resize events.
    """
    
    def __call__(self, canvas_resize_event: CanvasResizeEvent) -> None: 
        """Handle a canvas resize event."""
        ...
