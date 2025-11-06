import matplotlib.artist
import matplotlib.axes
from ..extra.bufferx import Bufferx as Bufferx
from gsp.core.camera import Camera as Camera
from gsp.core.visual_base import VisualBase as VisualBase
from gsp.types.transbuf import TransBuf as TransBuf
from gsp.visuals.pixels import Pixels
from gsp_matplotlib.renderer import MatplotlibRenderer as MatplotlibRenderer

class RendererPixels:
    @staticmethod
    def render(renderer: MatplotlibRenderer, axes: matplotlib.axes.Axes, visual: Pixels, model_matrix: TransBuf, camera: Camera) -> list[matplotlib.artist.Artist]: ...
    @staticmethod
    def create_artists(renderer: MatplotlibRenderer, axes: matplotlib.axes.Axes, visual: VisualBase, group_count: int) -> None: ...
    @staticmethod
    def destroy_artists(renderer: MatplotlibRenderer, axes: matplotlib.axes.Axes, visual: VisualBase, group_count: int) -> None: ...
