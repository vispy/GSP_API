"""Example of panning and zooming in Matplotlib using mouse events."""

# stdlib imports
from typing import Optional

# pip imports
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.backend_bases import MouseEvent


class PanAndZoom:
    """Class to handle panning and zooming in a Matplotlib Axes."""

    def __init__(self, mpl_axes: Axes, base_scale: float = 2.0) -> None:
        """Initialize the PanAndZoom handler."""
        self._mpl_axes: Axes = mpl_axes
        self._base_scale: float = base_scale
        self._button_press_x: Optional[float] = None
        self._button_press_y: Optional[float] = None

        # Connect events
        self._mpl_axes.figure.canvas.mpl_connect("scroll_event", self.zoom)  # type: ignore
        self._mpl_axes.figure.canvas.mpl_connect("button_press_event", self.on_press)  # type: ignore
        self._mpl_axes.figure.canvas.mpl_connect("button_release_event", self.on_release)  # type: ignore
        self._mpl_axes.figure.canvas.mpl_connect("motion_notify_event", self.on_motion)  # type: ignore

    def zoom(self, event: MouseEvent) -> None:
        """Zoom in or out around the mouse pointer."""
        # sanity check - ensure the event is within the axes
        assert event.xdata is not None, "MouseEvent xdata should not be None"
        assert event.ydata is not None, "MouseEvent ydata should not be None"

        cur_xlim: tuple[float, float] = self._mpl_axes.get_xlim()
        cur_ylim: tuple[float, float] = self._mpl_axes.get_ylim()
        scale_factor: float = 1 / self._base_scale if event.button == "up" else self._base_scale

        new_width: float = (cur_xlim[1] - cur_xlim[0]) * scale_factor
        new_height: float = (cur_ylim[1] - cur_ylim[0]) * scale_factor
        relx: float = (cur_xlim[1] - event.xdata) / (cur_xlim[1] - cur_xlim[0])
        rely: float = (cur_ylim[1] - event.ydata) / (cur_ylim[1] - cur_ylim[0])

        self._mpl_axes.set_xlim((event.xdata - new_width * (1 - relx), event.xdata + new_width * relx))
        self._mpl_axes.set_ylim((event.ydata - new_height * (1 - rely), event.ydata + new_height * rely))
        self._mpl_axes.figure.canvas.draw_idle()

    def on_press(self, event: MouseEvent) -> None:
        """Store the mouse press position."""
        if event.inaxes != self._mpl_axes:
            return
        # Store pixel coordinates instead of data coordinates
        self._button_press_x = event.x
        self._button_press_y = event.y

    def on_motion(self, event: MouseEvent) -> None:
        """Pan the plot based on mouse movement."""
        if self._button_press_x is None or self._button_press_y is None or event.inaxes != self._mpl_axes:
            return
        prev_x: float = self._button_press_x
        prev_y: float = self._button_press_y

        # Calculate delta in pixel coordinates
        dx_pixels: float = event.x - prev_x
        dy_pixels: float = event.y - prev_y

        # Convert pixel delta to data delta
        cur_xlim: tuple[float, float] = self._mpl_axes.get_xlim()
        cur_ylim: tuple[float, float] = self._mpl_axes.get_ylim()

        print(f"cur_xlim: {cur_xlim}, cur_ylim: {cur_ylim}")

        bbox = self._mpl_axes.get_window_extent()
        dx_data: float = -dx_pixels * (cur_xlim[1] - cur_xlim[0]) / bbox.width
        dy_data: float = -dy_pixels * (cur_ylim[1] - cur_ylim[0]) / bbox.height

        # Apply the pan
        self._mpl_axes.set_xlim((cur_xlim[0] + dx_data, cur_xlim[1] + dx_data))
        self._mpl_axes.set_ylim((cur_ylim[0] + dy_data, cur_ylim[1] + dy_data))

        # Update press position for continuous panning
        self._button_press_x = event.x
        self._button_press_y = event.y
        self._mpl_axes.figure.canvas.draw_idle()

    def on_release(self, event: MouseEvent) -> None:
        """Clear the stored mouse press position."""
        self._button_press_x = None
        self._button_press_y = None
        self._mpl_axes.figure.canvas.draw_idle()


def main():
    """Main function to demonstrate PanAndZoom functionality."""
    # Example Usage
    mpl_figure, mpl_axes = plt.subplots()
    mpl_axes.plot(range(-100, +100), [x**2 for x in range(-100, +100)])
    pan_zoom = PanAndZoom(mpl_axes)
    plt.show()


if __name__ == "__main__":
    main()
