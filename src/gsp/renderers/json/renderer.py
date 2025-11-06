# local imports
from gsp.core.camera import Camera
from gsp.core.canvas import Canvas
from gsp.core.viewport import Viewport
from gsp.core.visual_base import VisualBase
import gsp.renderers.json.gsp_messages_pydantic as gsp_messages
from gsp.visuals.points import Points


class JsonRenderer:
    def __init__(self, canvas: Canvas):
        self.canvas = canvas
        self.message_id_counter = 0

    def render(self, viewports: list[Viewport], visuals: list[VisualBase], cameras: list[Camera]):
        """Render the given viewports, visuals, and cameras to JSON messages."""
        messages = []

        # create canvas message
        canvas_msg = gsp_messages.CanvasCreate(
            command_name="CanvasCreate",
            message_id=self.get_message_id(),
            canvas_uuid=self.canvas._uuid,
            width=self.canvas._width,
            height=self.canvas._height,
            dpi=self.canvas._dpi,
        )
        messages.append(canvas_msg)

        # create viewport messages
        for viewport in viewports:
            # create viewport message
            viewport_msg = gsp_messages.ViewportCreate(
                command_name="ViewportCreate",
                message_id=self.get_message_id(),
                viewport_uuid=viewport._uuid,
                canvas_uuid=self.canvas._uuid,
                x=viewport.get_origin_x(),
                y=viewport.get_origin_y(),
                width=viewport._width,
                height=viewport._height,
            )
            messages.append(viewport_msg)

        # create visual messages
        for visual in visuals:
            if isinstance(visual, Points):
                self.render_points(visual)
                messages.extend(visual_msg)  # type: ignore

        return messages

    def get_message_id(self) -> int:
        """Get the next message ID."""
        self.message_id_counter += 1
        return self.message_id_counter

    def render_points(self, points: Points):
        """Render a Points visual to JSON messages."""
        visual_msg = []

        return visual_msg
