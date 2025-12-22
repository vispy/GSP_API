# stdlib imports
from typing import Optional

# pip imports
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.backend_bases import MouseEvent


class PanAndZoom:
    """Class to handle panning and zooming in a Matplotlib Axes."""

    def __init__(self, axes: Axes, base_scale: float = 2.0) -> None:
        """Initialize the PanAndZoom handler."""
        self._axes: Axes = axes
        self._base_scale: float = base_scale
        self._button_press_xy: Optional[tuple[float, float]] = None

        # Connect events
        self._axes.figure.canvas.mpl_connect("scroll_event", self.zoom)  # type: ignore
        self._axes.figure.canvas.mpl_connect("button_press_event", self.on_press)  # type: ignore
        self._axes.figure.canvas.mpl_connect("button_release_event", self.on_release)  # type: ignore
        self._axes.figure.canvas.mpl_connect("motion_notify_event", self.on_motion)  # type: ignore

    def zoom(self, event: MouseEvent) -> None:
        """Zoom in or out around the mouse pointer."""
        # sanity check - ensure the event is within the axes
        assert event.xdata is not None, "MouseEvent xdata should not be None"
        assert event.ydata is not None, "MouseEvent ydata should not be None"

        cur_xlim: tuple[float, float] = self._axes.get_xlim()
        cur_ylim: tuple[float, float] = self._axes.get_ylim()
        scale_factor: float = 1 / self._base_scale if event.button == "up" else self._base_scale

        new_width: float = (cur_xlim[1] - cur_xlim[0]) * scale_factor
        new_height: float = (cur_ylim[1] - cur_ylim[0]) * scale_factor
        relx: float = (cur_xlim[1] - event.xdata) / (cur_xlim[1] - cur_xlim[0])
        rely: float = (cur_ylim[1] - event.ydata) / (cur_ylim[1] - cur_ylim[0])

        self._axes.set_xlim((event.xdata - new_width * (1 - relx), event.xdata + new_width * relx))
        self._axes.set_ylim((event.ydata - new_height * (1 - rely), event.ydata + new_height * rely))
        self._axes.figure.canvas.draw_idle()

    def on_press(self, event: MouseEvent) -> None:
        """Store the mouse press position."""
        if event.inaxes != self._axes:
            return
        # Store pixel coordinates instead of data coordinates
        self._button_press_xy = event.x, event.y

    def on_motion(self, event: MouseEvent) -> None:
        """Pan the plot based on mouse movement."""
        if self._button_press_xy is None or event.inaxes != self._axes:
            return
        prev_x: float
        prev_y: float
        prev_x, prev_y = self._button_press_xy

        # Calculate delta in pixel coordinates
        dx_pixels: float = event.x - prev_x
        dy_pixels: float = event.y - prev_y

        # Convert pixel delta to data delta
        cur_xlim: tuple[float, float] = self._axes.get_xlim()
        cur_ylim: tuple[float, float] = self._axes.get_ylim()

        print(f"cur_xlim: {cur_xlim}, cur_ylim: {cur_ylim}")

        bbox = self._axes.get_window_extent()
        dx_data: float = -dx_pixels * (cur_xlim[1] - cur_xlim[0]) / bbox.width
        dy_data: float = -dy_pixels * (cur_ylim[1] - cur_ylim[0]) / bbox.height

        # Apply the pan
        self._axes.set_xlim((cur_xlim[0] + dx_data, cur_xlim[1] + dx_data))
        self._axes.set_ylim((cur_ylim[0] + dy_data, cur_ylim[1] + dy_data))

        # Update press position for continuous panning
        self._button_press_xy = event.x, event.y
        self._axes.figure.canvas.draw_idle()

    def on_release(self, event: MouseEvent) -> None:
        """Clear the stored mouse press position."""
        self._button_press_xy = None
        self._axes.figure.canvas.draw_idle()


# Example Usage
figure, axes = plt.subplots()
axes.plot(range(-100, +100), [x**2 for x in range(-100, +100)])
pan_zoom = PanAndZoom(axes)
plt.show()
