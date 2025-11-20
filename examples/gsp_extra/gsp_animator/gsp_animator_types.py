# stdlib imports
from typing import Callable, Sequence, Protocol

# local imports
from gsp.types.visual_base import VisualBase


# do a callback type for the animation loop
GSPAnimatorFunc = Callable[[float], Sequence[VisualBase]]
"""A simple animation loop manager for matplotlib rendering.

Arguments:
    delta_time (float): Time elapsed since the last frame in milliseconds.
"""


# TODO use the gsp.core.Event system instead?
class VideoSavedCalledback(Protocol):
    def __call__(self) -> None: ...  # type: ignore
