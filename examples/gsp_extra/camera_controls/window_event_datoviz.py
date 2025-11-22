#
# local imports
from .window_event_base import WindowEventBase


class WindowEventDatoviz(WindowEventBase):
    """Matplotlib window event handler for camera controls"""

    def __init__(self, dvz_panel):
        self._panel = dvz_panel

        # event connections
        self._dvz_press_cid: int | None = None
        self._dvz_release_cid: int | None = None
        self._dvz_motion_cid: int | None = None
        self._dvz_scroll_cid: int | None = None
