from typing import Protocol
from dataclasses import dataclass
from enum import StrEnum


class EventType(StrEnum):
    KEY_PRESS = "key_press"
    KEY_RELEASE = "key_release"
    BUTTON_PRESS = "button_press"
    BUTTON_RELEASE = "button_release"
    MOUSE_MOVE = "mouse_move"


@dataclass
class KeyboardEvent:
    event_type: EventType
    key_name: str


@dataclass
class MouseEvent:
    event_type: EventType
    x: float
    y: float
    left_button: bool = False
    middle_button: bool = False
    right_button: bool = False
    scroll_steps: float = 0.0


# We can define the expected function signature using a Protocol for clarity.
class KeyboardEventCallback(Protocol):
    def __call__(self, event: KeyboardEvent) -> None: ...


class MouseEventCallback(Protocol):
    def __call__(self, event: MouseEvent) -> None: ...
