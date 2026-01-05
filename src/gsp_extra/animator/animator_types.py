"""Type definitions for the animator module.

This module defines callback protocols and type aliases used by the animator
for managing animation loops and video saving operations.
"""

# stdlib imports
from typing import Callable, Sequence, Protocol

# local imports
from gsp.types.visual_base import VisualBase


# do a callback type for the animation loop
AnimatorFunc = Callable[[float], Sequence[VisualBase]]
"""Type alias for animation callback functions.

An animator function is called on each frame of the animation and returns
the sequence of visual elements to render for that frame.

Args:
    delta_time: Time elapsed since the last frame in milliseconds.

Returns:
    A sequence of VisualBase objects to render in the current frame.
"""


class VideoSavedCalledback(Protocol):
    """Callback protocol for video saved event."""

    def __call__(self) -> None: 
        """Called when the video has been successfully saved."""
        ...  
