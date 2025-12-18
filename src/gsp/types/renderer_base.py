"""Base class for renderers that display canvas scenes."""

# stdlib imports
from abc import ABC, abstractmethod
from typing import Sequence

# local imports
from gsp.core.canvas import Canvas
from gsp.core.viewport import Viewport
from gsp.types.visual_base import VisualBase
from gsp.core.camera import Camera
from gsp.types.transbuf import TransBuf


class RendererBase(ABC):
    """Abstract base class for rendering canvas scenes.

    This class defines the interface for renderers that display a canvas
    with viewports, visuals, model matrices, and cameras.
    """

    @abstractmethod
    def __init__(self, canvas: Canvas):
        """Initialize the renderer with the given canvas.

        Args:
            canvas: The canvas to render.
        """
        pass

    @abstractmethod
    def close(self) -> None:
        """Close the renderer and release any resources."""
        pass

    @abstractmethod
    def get_canvas(self) -> Canvas:
        """Return the associated canvas.

        Returns:
            The canvas associated with this renderer.
        """
        pass

    @abstractmethod
    def render(
        self,
        viewports: Sequence[Viewport],
        visuals: Sequence[VisualBase],
        model_matrices: Sequence[TransBuf],
        cameras: Sequence[Camera],
    ) -> bytes:
        """Render the given scene.

        Args:
            viewports: Sequence of viewport objects to render.
            visuals: Sequence of visual objects to render.
            model_matrices: Sequence of transformation buffers for model matrices.
            cameras: Sequence of camera objects to use for rendering.

        Returns:
            The rendered scene as bytes.
        """
        pass

    @abstractmethod
    def show(self) -> None:
        """Show the rendered canvas (blocking call)."""
        pass
