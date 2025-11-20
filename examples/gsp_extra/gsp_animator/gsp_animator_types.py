# stdlib imports
from typing import Callable, Sequence, Protocol

# local imports
import gsp


# do a callback type for the animation loop
GSPAnimatorFunc = Callable[[float], Sequence[gsp.core.VisualBase]]
"""A simple animation loop manager for matplotlib rendering.

Arguments:
    delta_time (float): Time elapsed since the last frame in milliseconds.
"""


class VideoSavedCalledback(Protocol):
    def __call__(self) -> None: ...  # type: ignore
