# stdlib imports
import os
import __main__
from typing import Sequence
import time

# pip imports
import matplotlib.animation
import matplotlib.artist

# local imports
import gsp
from gsp.types.transbuf import TransBuf
from gsp_matplotlib.renderer import MatplotlibRenderer
from gsp.types.visual_base import VisualBase
from gsp.core.canvas import Canvas
from gsp.core.viewport import Viewport
from gsp.core.camera import Camera
from gsp.visuals.points import Points
from gsp.visuals.texts import Texts
from gsp.core import Event
from .animator_types import AnimatorFunc, VideoSavedCalledback
from .animator_base import AnimatorBase

__dirname__ = os.path.dirname(os.path.abspath(__file__))


class AnimatorMatplotlib(AnimatorBase):
    """
    Animator for GSP scenes using a matplotlib renderer.
    """

    def __init__(
        self,
        matplotlib_renderer: MatplotlibRenderer,
        fps: int = 50,
        video_duration: float = 10.0,
        video_path: str | None = None,
        video_writer: str | None = None,
    ):
        self._callbacks: list[AnimatorFunc] = []
        self._matplotlib_renderer = matplotlib_renderer
        self._fps = fps
        self._video_duration = video_duration
        self._video_path = video_path
        self._video_writer: str | None = None
        self._time_last_update: float | None = None

        self._funcAnimation: matplotlib.animation.FuncAnimation | None = None

        self._canvas: Canvas | None = None
        self._viewports: Sequence[Viewport] | None = None
        self._visuals: Sequence[VisualBase] | None = None
        self._model_matrices: Sequence[TransBuf] | None = None
        self._cameras: Sequence[Camera] | None = None

        self.on_video_saved = Event[VideoSavedCalledback]()

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

    def add_callback(self, func: AnimatorFunc) -> None:
        """Add a callback to the animation loop."""
        self._callbacks.append(func)

    def remove_callback(self, func: AnimatorFunc) -> None:
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
    # .start()
    # =============================================================================
    def start(self, viewports: Sequence[Viewport], visuals: Sequence[VisualBase], model_matrices: Sequence[TransBuf], cameras: Sequence[Camera]) -> None:
        """
        Animate the given canvas and camera using the provided callbacks to update visuals.
        """

        self._canvas = self._matplotlib_renderer.get_canvas()
        self._viewports = viewports
        self._visuals = visuals
        self._model_matrices = model_matrices
        self._cameras = cameras
        self._time_last_update = time.time()

        # =============================================================================
        # Render the image once
        # =============================================================================

        self._matplotlib_renderer.render(viewports, visuals, model_matrices, cameras)

        # =============================================================================
        # Handle GSP_TEST=True
        # =============================================================================

        # detect if we are in not interactive mode - used during testing
        in_test = "GSP_TEST" in os.environ and os.environ["GSP_TEST"] == "True"

        # if we are not in interactive mode, save a preview image and return
        if in_test == True:
            # notify all animator callbacks
            changed_visuals: list[VisualBase] = []
            for animator_callback in self._callbacks:
                _changed_visuals = animator_callback(1.0 / self._fps)
                changed_visuals.extend(_changed_visuals)

            # render the scene to get the new image
            image_png_data = self._matplotlib_renderer.render(viewports, visuals, model_matrices, cameras, return_image=True, image_format="png")
            # get the main script name
            main_script_name = os.path.basename(__main__.__file__) if hasattr(__main__, "__file__") else "interactive"
            main_script_basename = os.path.splitext(main_script_name)[0]
            # buid the output image path
            image_path = os.path.join(__dirname__, "../../output", f"{main_script_basename}_animator_matplotlib.png")
            image_path = os.path.abspath(image_path)
            # save image_png_data in a image file
            with open(image_path, "wb") as image_file:
                image_file.write(image_png_data)
            # log the event
            print(f"Saved animation preview image to: {image_path}")
            return

        # NOTE: here we are in interactive mode!!

        # =============================================================================
        # Initialize the animation
        # =============================================================================

        figure = self._matplotlib_renderer.get_mpl_figure()
        self._funcAnimation = matplotlib.animation.FuncAnimation(
            figure, self._mpl_animate, frames=int(self._video_duration * self._fps), interval=1000.0 / self._fps
        )

        # save the animation if a path is provided
        if self._video_path is not None:
            self._funcAnimation.save(self._video_path, writer=self._video_writer, fps=self._fps)
            # Dispatch the video saved event
            self.on_video_saved.dispatch()

        # =============================================================================
        # Show the animation
        # =============================================================================

        self._matplotlib_renderer.show()

    # =============================================================================
    # .stop()
    # =============================================================================
    def stop(self):
        self._canvas = None
        self._viewports = None
        self._time_last_update = None

        # stop the animation function timer
        if self._funcAnimation is not None:
            self._funcAnimation.event_source.stop()
            self._funcAnimation = None

    # =============================================================================
    # ._mpl_animate()
    # =============================================================================

    def _mpl_animate(self, frame_index: int) -> list[matplotlib.artist.Artist]:
        # sanity checks
        assert self._canvas is not None, "Canvas MUST be set during the animation"
        assert self._viewports is not None, "Viewports MUST be set during the animation"
        assert self._visuals is not None, "Visuals MUST be set during the animation"
        assert self._model_matrices is not None, "Model matrices MUST be set during the animation"
        assert self._cameras is not None, "Cameras MUST be set during the animation"

        # compute delta time
        present = time.time()
        delta_time = (present - self._time_last_update) if self._time_last_update is not None else (1 / self._fps)
        self._time_last_update = present

        # notify all animator callbacks
        changed_visuals: list[VisualBase] = []
        for callback in self._callbacks:
            _changed_visuals = callback(delta_time)
            changed_visuals.extend(_changed_visuals)

        # Render the scene to update the visuals
        self._matplotlib_renderer.render(self._viewports, self._visuals, self._model_matrices, self._cameras)

        # convert all changed visuals to mpl artists
        changed_mpl_artists: list[matplotlib.artist.Artist] = []
        for visual in changed_visuals:
            mpl_artists = self._get_mpl_artists(self._viewports, self._visuals, visual)
            changed_mpl_artists.extend(mpl_artists)

        # return the changed mpl artists
        return changed_mpl_artists

    # =============================================================================
    # ._get_mpl_artists()
    # =============================================================================

    def _get_mpl_artists(self, viewports: Sequence[Viewport], visuals: Sequence[VisualBase], visual_base: VisualBase) -> list[matplotlib.artist.Artist]:
        """
        Get the matplotlib artists corresponding to a given visual in the canvas.
        This is needed for the matplotlib FuncAnimation to update only the relevant artists.
        """

        mpl_artists: list[matplotlib.artist.Artist] = []

        # Find the index of the visual in the visuals list
        visual_index = visuals.index(visual_base)
        visual = visuals[visual_index]
        viewport = viewports[visual_index]

        if isinstance(visual, Points):
            points: Points = visual
            artist_uuid = f"{viewport.get_uuid()}_{points.get_uuid()}"
            mpl_artist = self._matplotlib_renderer._artists[artist_uuid]
            mpl_artists.append(mpl_artist)
        elif isinstance(visual, Texts):
            texts: Texts = visual
            for text_index in range(len(texts.get_strings())):
                artist_uuid = f"{viewport.get_uuid()}_{texts.get_uuid()}_{text_index}"
                mpl_artist = self._matplotlib_renderer._artists[artist_uuid]
                mpl_artists.append(mpl_artist)
        else:
            raise NotImplementedError(f"Getting mpl artists for visual type {type(visual)} is not implemented.")

        return mpl_artists
