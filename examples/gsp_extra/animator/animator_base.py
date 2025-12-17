"""Abstract base class for GSP scene animators."""

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
    """Abstract base class for GSP scene animators.
    
    Defines the interface for animator implementations that handle frame-by-frame
    updates of GSP visualizations. Concrete implementations should provide
    renderer-specific animation loop mechanisms.
    """

    __slots__ = ()

    on_video_saved: Event[VideoSavedCalledback]
    """Event triggered when the video is saved."""

    @abstractmethod
    def add_callback(self, func: AnimatorFunc) -> None:
        """Add a callback to the animation loop.
        
        Args:
            func: The callback function to add. It should accept a delta_time float
                  and return a sequence of VisualBase objects that were modified.
        """
        pass

    @abstractmethod
    def remove_callback(self, func: AnimatorFunc) -> None:
        """Remove a callback from the animation loop.
        
        Args:
            func: The callback function to remove. Must be the same function
                  object that was previously added.
        """
        pass

    @abstractmethod
    def event_listener(self, func: AnimatorFunc) -> AnimatorFunc:
        """Decorator to register a callback function to the animation loop.
        
        This method should be implemented to allow decorator-style registration
        of animation callbacks.
        
        Args:
            func: The callback function to decorate and add to the animation loop.
                  Should accept delta_time (float) and return a sequence of modified VisualBase objects.
                  
        Returns:
            The wrapper function that will be called on each animation frame.
        """
        pass

    @abstractmethod
    def start(self, viewports: Sequence[Viewport], visuals: Sequence[VisualBase], model_matrices: Sequence[TransBuf], cameras: Sequence[Camera]) -> None:
        """Start the animation loop.
        
        Begins animating the scene using the provided viewports, visuals, model matrices,
        and cameras. The registered callbacks will be invoked on each frame to update
        the scene.
        
        Args:
            viewports: Sequence of viewports to render.
            visuals: Sequence of visual objects to animate.
            model_matrices: Sequence of transformation buffers for the visuals.
            cameras: Sequence of cameras for each viewport.
        """
        pass

    @abstractmethod
    def stop(self) -> None:
        """Stop the animation loop.
        
        Cleans up animation state and stops any ongoing animation.
        """
        pass
