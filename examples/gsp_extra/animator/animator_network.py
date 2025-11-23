# stdlib imports
import io
import os
import __main__
import time
from typing import Sequence

# pip imports
import numpy as np
import matplotlib.pyplot
import matplotlib.image
import matplotlib.animation
import matplotlib.artist
import matplotlib.figure

# local imports
from gsp_network.renderer import NetworkRenderer
from gsp.types.visual_base import VisualBase
from gsp.types.transbuf import TransBuf
from gsp.core.event import Event
from gsp.core import Viewport, Camera, Canvas
from .animator_types import AnimatorFunc, VideoSavedCalledback

__dirname__ = os.path.dirname(os.path.abspath(__file__))


class GspAnimatorNetwork:
    """
    Animator for GSP scenes using a network renderer and matplotlib for display.

    Note: this requires a running GSP server. See the README for instructions.
    IMPORTANT: it DOES NOT depends on GSP matplotlib renderer, it only uses pip matplotlib to display
    """

    on_video_saved = Event[VideoSavedCalledback]()
    """Event triggered when the video is saved."""

    def __init__(
        self,
        network_renderer: NetworkRenderer,
        fps: int = 30,
        video_duration: float = 10.0,
        video_path: str | None = None,
        video_writer: str | None = None,
    ):
        self._callbacks: list[AnimatorFunc] = []
        self._network_renderer = network_renderer
        self._fps = fps
        self._video_duration = video_duration
        self._video_path = video_path
        self._video_writer: str | None = None
        self._time_last_update = None

        self._funcAnimation: matplotlib.animation.FuncAnimation | None = None
        self._axes_image: matplotlib.image.AxesImage | None = None

        self._viewports: Sequence[Viewport] | None = None
        self._visuals: Sequence[VisualBase] | None = None
        self._model_matrices: Sequence[TransBuf] | None = None
        self._cameras: Sequence[Camera] | None = None

        self._canvas: Canvas = self._network_renderer.get_canvas()
        # Create a figure
        figure_width = self._canvas.get_width() / self._canvas.get_dpi()
        figure_height = self._canvas.get_height() / self._canvas.get_dpi()
        self._figure: matplotlib.figure.Figure = matplotlib.pyplot.figure(figsize=(figure_width, figure_height), dpi=self._canvas.get_dpi())
        assert self._figure.canvas.manager is not None, f"matplotlib figure canvas manager is None"
        self._figure.canvas.manager.set_window_title(f"Network ({self._network_renderer.get_remote_renderer_name()}) Animator")

        # guess the video writer from the file extension if not provided
        if self._video_path is not None:
            if video_writer is not None:
                self._video_writer = video_writer
            else:
                video_ext = os.path.splitext(self._video_path)[1].lower()
                if video_ext in [".mp4", ".m4v", ".mov"]:
                    self._video_writer = "ffmpeg"
                elif video_ext in [".gif", ".apng", ".webp"]:
                    self._video_writer = "pillow"
                else:
                    raise ValueError(f"Unsupported video format: {video_ext}")

    # =============================================================================
    # .add_callback/.remove_callback/.decorator
    # =============================================================================

    def add_callback(self, func: AnimatorFunc):
        """Add a callback to the animation loop."""
        self._callbacks.append(func)

    def remove_callback(self, func: AnimatorFunc):
        """Remove a callback from the animation loop."""
        self._callbacks.remove(func)

    def event_listener(self, func: AnimatorFunc) -> AnimatorFunc:
        """A decorator to add a callback to the animation loop.

        Usage:
            ```python
                @animation_loop.event_listener
                def my_callback(delta_time: float) -> Sequence[Object3D]:
                    ...

                # later, if needed
                animation_loop.remove_callback(my_callback)
            ```
        """

        self.add_callback(func)

        def wrapper(delta_time: float) -> Sequence[VisualBase]:
            # print("Before the function runs")
            result = func(delta_time)
            # print("After the function runs")
            return result

        return wrapper

    # =============================================================================
    # .animate
    # =============================================================================
    def start(self, viewports: Sequence[Viewport], visuals: Sequence[VisualBase], model_matrices: Sequence[TransBuf], cameras: Sequence[Camera]):
        """
        Animate the given canvas and camera using the provided callbacks to update visuals.
        """

        self._viewports = viewports
        self._visuals = visuals
        self._model_matrices = model_matrices
        self._cameras = cameras
        self._time_last_update = time.time()

        # get the only axes in the figure
        mpl_axes = self._figure.add_axes((0, 0, 1, 1))
        # hide the borders
        mpl_axes.axis("off")

        # create an np.array to hold the image
        image_data_np = np.zeros((self._canvas.get_height(), self._canvas.get_width(), 3), dtype=np.uint8)
        self._axes_image = mpl_axes.imshow(image_data_np)

        # =============================================================================
        # Handle GSP_INTERACTIVE_MODE is False
        # =============================================================================

        # detect if we are in not interactive mode - used during testing
        gsp_interactive_mode = "GSP_INTERACTIVE_MODE" not in os.environ or os.environ["GSP_INTERACTIVE_MODE"] != "False"
        if gsp_interactive_mode is False:
            # notify all animator callbacks
            changed_visuals: list[VisualBase] = []
            for animator_callback in self._callbacks:
                _changed_visuals = animator_callback(1.0 / self._fps)
                changed_visuals.extend(_changed_visuals)

            # render the scene to get the new image
            image_png_data = self._network_renderer.render(self._viewports, self._visuals, self._model_matrices, self._cameras)
            # get the main script name
            main_script_name = os.path.basename(__main__.__file__) if hasattr(__main__, "__file__") else "interactive"
            main_script_basename = os.path.splitext(main_script_name)[0]
            # buid the output image path
            image_path = os.path.join(__dirname__, "../../output", f"{main_script_basename}_animator.png")
            image_path = os.path.abspath(image_path)
            # save image_png_data in a image file
            with open(image_path, "wb") as image_file:
                image_file.write(image_png_data)
            # log the event
            print(f"Saved animation preview image to: {image_path}")
            return

        # =============================================================================
        # Initialize the animation
        # =============================================================================
        self._funcAnimation = matplotlib.animation.FuncAnimation(
            self._figure, self._mpl_animate, frames=int(self._video_duration * self._fps), interval=1000.0 / self._fps
        )
        # save the animation if a path is provided
        if self._video_path is not None:
            self._funcAnimation.save(self._video_path, writer=self._video_writer, fps=self._fps)
            # Dispatch the video saved event
            self.on_video_saved.dispatch()

        # show the animation
        matplotlib.pyplot.show()

        print("Animation finished")

    # =============================================================================
    # .stop()
    # =============================================================================
    def stop(self):
        # self._canvas = None
        self._viewports = None
        self._cameras = None
        self._time_last_update = None

        # stop the animation function timer
        if self._funcAnimation is not None:
            # NOTE: MUST be done before closing the figure
            self._funcAnimation.event_source.stop()
            self._funcAnimation = None

        if self._figure is not None:
            matplotlib.pyplot.close(self._figure)
            # self._figure = None

    # =============================================================================
    # Animation function
    # =============================================================================

    # function called at each animation frame
    def _mpl_animate(self, frame_index: int) -> Sequence[matplotlib.artist.Artist]:
        # compute delta time
        present = time.time()
        delta_time = (present - self._time_last_update) if self._time_last_update is not None else (1 / self._fps)
        self._time_last_update = present

        # notify all animator callbacks
        changed_visuals: list[VisualBase] = []
        for animator_callback in self._callbacks:
            _changed_visuals = animator_callback(delta_time)
            changed_visuals.extend(_changed_visuals)

        # sanity checks
        assert self._viewports is not None, f"PANIC self._viewports is None"
        assert self._visuals is not None, f"PANIC self._visuals is None"
        assert self._model_matrices is not None, f"PANIC self._model_matrices is None"
        assert self._cameras is not None, f"PANIC self._cameras is None"

        # render the scene to get the new image
        image_png_data = self._network_renderer.render(self._viewports, self._visuals, self._model_matrices, self._cameras)
        image_data_io = io.BytesIO(image_png_data)
        image_data_np = matplotlib.image.imread(image_data_io, format="png")

        assert self._axes_image is not None, f"PANIC self._axes_image is None"
        # update the image data
        self._axes_image.set_data(image_data_np)

        # return the changed mpl artists
        changed_mpl_artists = [self._axes_image]
        return changed_mpl_artists

    def get_mpl_figure(self) -> matplotlib.figure.Figure:
        """Get the matplotlib figure used for the animation."""
        return self._figure
