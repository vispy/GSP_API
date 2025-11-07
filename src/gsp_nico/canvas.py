from gsp.core import Canvas as GspCanvas


class Canvas:
    def __init__(self, width: int, height: int, dpi: float):
        self.gsp_canvas = GspCanvas(width, height, dpi)

        self.viewports = []

    def add(self, viewport):
        self.viewports.append(viewport)
