import matplotlib.artist
import matplotlib.axes
from ..extra.bufferx import Bufferx as Bufferx
from .renderer import MatplotlibRenderer as MatplotlibRenderer
from gsp.core.camera import Camera as Camera
from gsp.types.buffer_type import BufferType as BufferType
from gsp.types.transbuf import TransBuf as TransBuf
from gsp.visuals import pixels as pixels
from gsp.visuals.points import Points as Points

class RendererPoints:
    @staticmethod
    def render(renderer: MatplotlibRenderer, axes: matplotlib.axes.Axes, visual: Points, model_matrix: TransBuf, camera: Camera) -> list[matplotlib.artist.Artist]: ...
