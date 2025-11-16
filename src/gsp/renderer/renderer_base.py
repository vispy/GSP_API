# stdlib imports
from abc import ABC, abstractmethod
from typing import Sequence

# local imports
from gsp.core.canvas import Canvas
from gsp.core.viewport import Viewport
from gsp.core.visual_base import VisualBase
from gsp.core.camera import Camera
from gsp.types.transbuf import TransBuf


class RendererBase(ABC):
    @abstractmethod
    def __init__(self, canvas: Canvas):
        pass

    @abstractmethod
    def render(
        self,
        viewports: Sequence[Viewport],
        visuals: Sequence[VisualBase],
        model_matrices: Sequence[TransBuf],
        cameras: Sequence[Camera],
    ) -> bytes | str:
        pass
