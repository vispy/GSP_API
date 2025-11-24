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
from gsp_network.renderer import NetworkRenderer
from .viewport_events_types import KeyEvent, MouseEvent, EventType
from .viewport_events_base import ViewportEventsBase
from .viewport_events_types import KeyEvent, MouseEvent, KeyboardEventCallback, MouseEventCallback


class ViewportEventsNetwork(ViewportEventsBase):
    """NetworkRenderer event handler for viewport"""

    __slots__ = ("_renderer", "_viewport")

    def __init__(self, renderer: NetworkRenderer, viewport: Viewport) -> None:

        self._renderer: NetworkRenderer = renderer
        self._viewport: Viewport = viewport

    def close(self):
        pass
