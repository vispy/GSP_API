from gsp.core import Canvas as GspCanvas


class Canvas:
    def __init__(self, width: int, height: int, dpi: float):
        self.gsp_canvas = GspCanvas(width, height, dpi)

        self.untyped_viewports: list = []
        """untyped to avoid circular import issues"""

    def add(self, viewport):
        self.untyped_viewports.append(viewport)
