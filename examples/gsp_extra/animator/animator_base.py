# stdlib imports
from abc import ABC, abstractmethod
from typing import Sequence

# local imports
from gsp.core import Event
from gsp.core.viewport import Viewport
from gsp.core.camera import Camera
from gsp.types.visual_base import VisualBase
from gsp.types.transbuf import TransBuf
from .animator_types import AnimatorFunc, VideoSavedCalledback


class AnimatorBase(ABC):
    """Base class for window event handlers for camera controls"""

    __slots__ = ()

    on_video_saved: Event[VideoSavedCalledback]
    """Event triggered when the video is saved."""

    @abstractmethod
    def add_callback(self, func: AnimatorFunc) -> None:
        """Add a callback to the animation loop."""
        pass

    @abstractmethod
    def remove_callback(self, func: AnimatorFunc) -> None:
        """Remove a callback from the animation loop."""
        pass

    @abstractmethod
    def event_listener(self, func: AnimatorFunc) -> AnimatorFunc:
        pass

    @abstractmethod
    def start(self, viewports: Sequence[Viewport], visuals: Sequence[VisualBase], model_matrices: Sequence[TransBuf], cameras: Sequence[Camera]) -> None:
        pass

    @abstractmethod
    def stop(self) -> None:
        pass
