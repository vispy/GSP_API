import numpy as np

from gsp.core import Viewport as GspViewport
from gsp.types import Buffer as GspBuffer
from gsp.types.buffer_type import BufferType as GspBufferType
from gsp_matplotlib.extra.bufferx import Bufferx
from gsp_nico.pixels import Pixels
from gsp_nico.canvas import Canvas


class Viewport:
    def __init__(self, canvas: Canvas, x: int, y: int, width: int, height: int):
        self.canvas = canvas
        self.gsp_viewport = GspViewport(x, y, width, height)

        canvas.add(self)
        self.visuals: list[Pixels] = []
        self.gsp_view_matrices: list[GspBuffer] = []
        self.gsp_proj_matrices: list[GspBuffer] = []

    def add(self, visual: Pixels, view_matrix: np.ndarray, proj_matrix: np.ndarray):
        self.visuals.append(visual)
        gsp_view_matrix = Bufferx.from_numpy(np.asarray([view_matrix]), GspBufferType.mat4)
        gsp_proj_matrix = Bufferx.from_numpy(np.asarray([proj_matrix]), GspBufferType.mat4)
        self.gsp_view_matrices.append(gsp_view_matrix)
        self.gsp_proj_matrices.append(gsp_proj_matrix)
