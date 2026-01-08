"""Animator for GSP scenes using a matplotlib renderer."""

# stdlib imports
from logging import warning
import os
import __main__
from typing import Sequence
import time

# local imports
from gsp.types.transbuf import TransBuf
from gsp_datoviz.renderer.datoviz_renderer import DatovizRenderer
from gsp.types.visual_base import VisualBase
from gsp.core.canvas import Canvas
from gsp.core.viewport import Viewport
from gsp.core.camera import Camera
from gsp.core import Event
from gsp.types.animator_types import AnimatorFunc, VideoSavedCalledback
from gsp.types.animator_base import AnimatorBase

__dirname__ = os.path.dirname(os.path.abspath(__file__))


class AnimatorDatoviz(AnimatorBase):
    """Animator for GSP scenes using a matplotlib renderer."""

    def __init__(
        self,
        datoviz_renderer: DatovizRenderer,
        fps: int = 50,
        video_duration: float | None = None,
        video_path: str | None = None,
    ):
        """Initialize the animator.

        Args:
            datoviz_renderer (DatovizRenderer): The datoviz renderer to use for rendering.
            fps (int, optional): Frames per second. Defaults to 50.
            video_duration (float | None, optional): Duration of the video to save. Defaults to None.
            video_path (str | None, optional): Path to save the video. Defaults to None.
        """
        self._callbacks: list[AnimatorFunc] = []
        self._datoviz_renderer = datoviz_renderer
        self._fps = fps

        # sanity check - video not supported yet
        assert video_duration is None, "GspAnimatorDatoviz does not support video saving yet."
        assert video_path is None, "GspAnimatorDatoviz does not support video saving yet."

        self._canvas: Canvas | None = None
        self._viewports: Sequence[Viewport] | None = None
        self._visuals: Sequence[VisualBase] | None = None
        self._model_matrices: Sequence[TransBuf] | None = None
        self._cameras: Sequence[Camera] | None = None

        self.on_video_saved = Event[VideoSavedCalledback]()
        """Event triggered when the video is saved."""

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
        """Animate the given canvas and camera using the provided callbacks to update visuals."""
        self._canvas = self._datoviz_renderer.get_canvas()
        self._viewports = viewports
        self._visuals = visuals
        self._model_matrices = model_matrices
        self._cameras = cameras
        self._time_last_update = time.time()

        # =============================================================================
        # Render the image once
        # =============================================================================

        self._datoviz_renderer.render(viewports, visuals, model_matrices, cameras)

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
            image_png_data = self._datoviz_renderer.render(viewports, visuals, model_matrices, cameras, return_image=True, image_format="png")
            # get the main script name
            main_script_name = os.path.basename(__main__.__file__) if hasattr(__main__, "__file__") else "interactive"
            main_script_basename = os.path.splitext(main_script_name)[0]
            # buid the output image path
            image_path = os.path.join(__dirname__, "../../../examples/output", f"{main_script_basename}_animator_datoviz.png")
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

        dvz_app = self._datoviz_renderer.get_dvz_app()

        @dvz_app.timer(period=1.0 / self._fps)
        def on_timer(event):
            self._dvz_animate()

        # =============================================================================
        # Show the animation
        # =============================================================================

        self._datoviz_renderer.show()

    # =============================================================================
    # .stop()
    # =============================================================================
    def stop(self):
        """Stop the animation."""
        self._canvas = None
        self._viewports = None
        self._time_last_update = None

        warning.warn("GspAnimatorDatoviz.stop() is not fully implemented yet.")

    def _dvz_animate(self) -> None:
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

        # changed_visuals is not used by datoviz, but could be used in the future

        # Render the scene to update the visuals
        self._datoviz_renderer.render(self._viewports, self._visuals, self._model_matrices, self._cameras, return_image=False)
