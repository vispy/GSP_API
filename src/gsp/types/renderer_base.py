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
    @abstractmethod
    def __init__(self, canvas: Canvas):
        """Initialize the renderer with the given canvas."""
        pass

    @abstractmethod
    def close(self) -> None:
        """Close the renderer and release any resources."""
        pass

    @abstractmethod
    def get_canvas(self) -> Canvas:
        """Return the associated canvas."""
        pass

    @abstractmethod
    def render(
        self,
        viewports: Sequence[Viewport],
        visuals: Sequence[VisualBase],
        model_matrices: Sequence[TransBuf],
        cameras: Sequence[Camera],
    ) -> bytes:
        """Render the given scene."""
        pass

    @abstractmethod
    def show(self) -> None:
        """Show the rendered canvas (blocking call)."""
        pass
