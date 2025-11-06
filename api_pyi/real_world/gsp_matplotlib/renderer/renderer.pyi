import matplotlib.axes
from _typeshed import Incomplete
from gsp.core.camera import Camera as Camera
from gsp.core.canvas import Canvas as Canvas
from gsp.core.viewport import Viewport as Viewport
from gsp.core.visual_base import VisualBase as VisualBase
from gsp.types import Buffer as Buffer
from gsp.types.transbuf import TransBuf as TransBuf
from typing import Sequence

class MatplotlibRenderer:
    canvas: Incomplete
    def __init__(self, canvas: Canvas) -> None: ...
    def render(self, viewports: Sequence[Viewport], visuals: Sequence[VisualBase], model_matrices: Sequence[TransBuf], cameras: Sequence[Camera]): ...
    def get_axes_for_viewport(self, viewport: Viewport) -> matplotlib.axes.Axes: ...
