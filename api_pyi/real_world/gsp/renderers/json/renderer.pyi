from _typeshed import Incomplete
from gsp.core.camera import Camera as Camera
from gsp.core.canvas import Canvas as Canvas
from gsp.core.viewport import Viewport as Viewport
from gsp.core.visual_base import VisualBase as VisualBase
from gsp.visuals.points import Points as Points

class JsonRenderer:
    canvas: Incomplete
    message_id_counter: int
    def __init__(self, canvas: Canvas) -> None: ...
    def render(self, viewports: list[Viewport], visuals: list[VisualBase], cameras: list[Camera]): ...
    def get_message_id(self) -> int: ...
    def render_points(self, points: Points): ...
