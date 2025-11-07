from gsp.core import Canvas as GspCanvas
from gsp_nico.viewport import Viewport


class Canvas:
    def __init__(self, width: int, height: int, dpi: float):
        self.gsp_canvas = GspCanvas(width, height, dpi)

        self.viewports: list[Viewport] = []

    def add(self, viewport: Viewport):
        self.viewports.append(viewport)
