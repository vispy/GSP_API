from gsp.types import Buffer as GspBuffer
from gsp.visuals.pixels import Pixels as GspPixels
from gsp_matplotlib.extra.bufferx import Bufferx

from .buffer import Buffer


class Pixels:
    def __init__(self, coords: GspBuffer, colors: GspBuffer):
        self.gsp_pixels = GspPixels(coords, colors, 1)
        self.gsp_model_matrix = Bufferx.mat4_identity()
