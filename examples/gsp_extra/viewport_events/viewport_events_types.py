from typing import Protocol
from dataclasses import dataclass
from enum import StrEnum


class EventType(StrEnum):
    KEY_PRESS = "key_press"
    KEY_RELEASE = "key_release"
    BUTTON_PRESS = "button_press"
    BUTTON_RELEASE = "button_release"
    MOUSE_MOVE = "mouse_move"
    MOUSE_SCROLL = "mouse_scroll"
    CANVAS_RESIZE = "canvas_resize"


@dataclass
class KeyEvent:
    viewport_uuid: str
    event_type: EventType
    key_name: str


@dataclass
class MouseEvent:
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
    viewport_uuid: str
    event_type: EventType
    canvas_width_px: int
    canvas_height_px: int


# We can define the expected function signature using a Protocol for clarity.
class KeyboardEventCallback(Protocol):
    def __call__(self, key_event: KeyEvent) -> None: ...


class MouseEventCallback(Protocol):
    def __call__(self, mouse_event: MouseEvent) -> None: ...


class CanvasResizeEventCallback(Protocol):
    def __call__(self, canvas_resize_event: CanvasResizeEvent) -> None: ...
