# stdlib imports
from types import FrameType
from typing import Any
import typing
import inspect

# pip imports
import matplotlib.figure
import matplotlib.axes
import matplotlib.backend_bases


# local imports
from gsp.core import Event
from gsp.core import Canvas, Viewport
from gsp_datoviz.renderer import DatovizRenderer
from .viewport_events_types import KeyEvent, MouseEvent, EventType
from .viewport_event_base import ViewportEventBase
from .viewport_events_types import KeyEvent, MouseEvent, KeyboardEventCallback, MouseEventCallback


class ViewportEventsDatoviz(ViewportEventBase):
    """DatovizRenderer event handler for viewport"""

    __slots__ = ("_renderer", "_viewport")

    def __init__(self, renderer: DatovizRenderer, viewport: Viewport) -> None:

        self._renderer: DatovizRenderer = renderer
        self._viewport: Viewport = viewport

    def close(self):
        pass
