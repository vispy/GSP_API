import matplotlib.figure
import matplotlib.backend_bases

from .window_event_base import WindowEventBase


class WindowEventMatplotlib(WindowEventBase):
    """Matplotlib window event handler for camera controls"""

    pass

    def __init__(self, mpl_figure: matplotlib.figure.Figure):
        self._figure = mpl_figure

        # event connections
        self._mpl_press_cid: int | None = None
        self._mpl_release_cid: int | None = None
        self._mpl_motion_cid: int | None = None
        self._mpl_scroll_cid: int | None = None

    def _connect(self):
        mpl_canvas: matplotlib.backend_bases.FigureCanvasBase = self._figure.canvas
        self._mpl_press_cid = mpl_canvas.mpl_connect("button_press_event", self._on_button_press)
        self._mpl_release_cid = mpl_canvas.mpl_connect("button_release_event", self._on_button_release)
        self._mpl_motion_cid = mpl_canvas.mpl_connect("motion_notify_event", self._on_mouse_move)
        self._mpl_scroll_cid = mpl_canvas.mpl_connect("scroll_event", self._on_scroll)

    def _disconnect(self):
        mpl_canvas: matplotlib.backend_bases.FigureCanvasBase = self._figure.canvas
        if self._mpl_press_cid is not None:
            mpl_canvas.mpl_disconnect(self._mpl_press_cid)
            self._mpl_press_cid = None
        if self._mpl_release_cid is not None:
            mpl_canvas.mpl_disconnect(self._mpl_release_cid)
            self._mpl_release_cid = None
        if self._mpl_motion_cid is not None:
            mpl_canvas.mpl_disconnect(self._mpl_motion_cid)
            self._mpl_motion_cid = None
        if self._mpl_scroll_cid is not None:
            mpl_canvas.mpl_disconnect(self._mpl_scroll_cid)
            self._mpl_scroll_cid = None

    def _on_button_press(self, event):
        pass

    def _on_button_release(self, event):
        pass

    def _on_mouse_move(self, event):
        pass

    def _on_scroll(self, event):
        pass
