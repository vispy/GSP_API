# stdlib imports
import os
import __main__
from typing import Sequence

# pip imports
import matplotlib.pyplot
import matplotlib.animation
import matplotlib.artist
import time

# local imports
import gsp
from gsp.types.transbuf import TransBuf
from gsp_matplotlib.renderer import MatplotlibRenderer
from gsp.types.visual_base import VisualBase
from gsp.core.canvas import Canvas
from gsp.core.viewport import Viewport
from gsp.core.camera import Camera
from .gsp_animator_types import GSPAnimatorFunc, VideoSavedCalledback

__dirname__ = os.path.dirname(os.path.abspath(__file__))


class GspAnimatorMatplotlib:
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
        self._callbacks: list[GSPAnimatorFunc] = []
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

        self.on_video_saved = gsp.core.Event[VideoSavedCalledback]()
        """Event triggered when the video is saved."""

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

    def add_callback(self, func: GSPAnimatorFunc):
        """Add a callback to the animation loop."""
        self._callbacks.append(func)

    def remove_callback(self, func: GSPAnimatorFunc):
        """Remove a callback from the animation loop."""
        self._callbacks.remove(func)

    def event_listener(self, func: GSPAnimatorFunc) -> GSPAnimatorFunc:
        """A decorator to add a callback to the animation loop.

        Usage:
            ```python
                @animation_loop.decorator
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
    def start(
        self, viewports: Sequence[Viewport], visuals: Sequence[VisualBase], model_matrices: Sequence[TransBuf], cameras: Sequence[Camera], block: bool = True
    ) -> None:
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
        # matplotlib animation callback
        # =============================================================================

        figure = self._matplotlib_renderer.get_mpl_figure()

        # =============================================================================
        # Handle GSP_INTERACTIVE_MODE=False
        # =============================================================================

        # detect if we are in not interactive mode - used during testing
        gsp_interactive_mode = "GSP_INTERACTIVE_MODE" not in os.environ or os.environ["GSP_INTERACTIVE_MODE"] != "False"

        # if we are not in interactive mode, save a preview image and return
        if gsp_interactive_mode == False:
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
            image_path = os.path.join(__dirname__, "../../output", f"{main_script_basename}_animator.png")
            image_path = os.path.abspath(image_path)
            # save image_png_data in a image file
            with open(image_path, "wb") as image_file:
                image_file.write(image_png_data)
            # log the event
            print(f"Saved animation preview image to: {image_path}")
            return

        # NOTE: here we are in interactive mode!!

        # =============================================================================
        # Connect cameras
        # =============================================================================
        # FIXME how to handle camera?
        # # connect the camera events to the render function
        # def camera_update(transform) -> None:
        #     self._matplotlib_renderer.render(canvas, viewports, cameras)

        # for camera, viewport in zip(cameras, canvas.viewports):
        #     mpl_axes = self._matplotlib_renderer._axes[viewport.uuid]
        #     camera.mpl3d_camera.connect(mpl_axes, camera_update)

        # =============================================================================
        # Initialize the animation
        # =============================================================================

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

        if block is True:
            matplotlib.pyplot.show()

    # =============================================================================
    # .stop()
    # =============================================================================
    def stop(self):
        # disconnect the cameras connected in .start()
        # FIXME how to handle camera?
        # if self._cameras is not None:
        #     for camera in self._cameras:
        #         camera.mpl3d_camera.disconnect()
        #     self._cameras = None

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
        # compute delta time
        present = time.time()
        delta_time = (present - self._time_last_update) if self._time_last_update is not None else (1 / self._fps)
        self._time_last_update = present

        # notify all animator callbacks
        changed_visuals: list[VisualBase] = []

        for callback in self._callbacks:
            _changed_visuals = callback(delta_time)
            changed_visuals.extend(_changed_visuals)

        # convert all changed visuals to mpl artists
        changed_mpl_artists: list[matplotlib.artist.Artist] = []
        for visual in changed_visuals:
            assert self._canvas is not None, "Canvas MUST be set during the animation"
            mpl_artist = self._get_mpl_artists(self._canvas, visual)
            changed_mpl_artists.append(mpl_artist)

        # return the changed mpl artists
        return changed_mpl_artists

    # =============================================================================
    # ._get_mpl_artists()
    # =============================================================================

    # TODO move that in the matplotlib renderer?
    def _get_mpl_artists(self, canvas: gsp.core.Canvas, visual_base: VisualBase) -> matplotlib.artist.Artist:
        """
        Get the matplotlib artists corresponding to a given visual in the canvas.
        This is needed for the matplotlib FuncAnimation to update only the relevant artists.
        """
        # FIXME implement this properly
        raise NotImplementedError("GspAnimatorMatplotlib._get_mpl_artists() is not implemented yet")
        # for viewport in canvas.viewports:
        #     for visual in viewport.visuals:
        #         # if it is not the visual we are looking for, skip it
        #         if visual != visual_base:
        #             continue

        #         # get the mpl artist corresponding to the visual
        #         if isinstance(visual, gsp.visuals.Image):
        #             image: gsp.visuals.Image = visual
        #             full_uuid = image.uuid + viewport.uuid
        #             assert full_uuid in self._matplotlib_renderer._axesImages, "Image not found in renderer"
        #             mpl_artist = self._matplotlib_renderer._axesImages[full_uuid]
        #             return mpl_artist
        #         elif isinstance(visual, gsp.visuals.Pixels):
        #             pixels: gsp.visuals.Pixels = visual
        #             full_uuid = pixels.uuid + viewport.uuid
        #             assert full_uuid in self._matplotlib_renderer._pathCollections, "Pixels not found in renderer"
        #             patchCollections = self._matplotlib_renderer._pathCollections[full_uuid]
        #             mpl_artist = patchCollections
        #             return mpl_artist
        #         elif isinstance(visual, gsp.visuals.Mesh):
        #             mesh: gsp.visuals.Mesh = visual
        #             full_uuid = mesh.uuid + viewport.uuid
        #             assert full_uuid in self._matplotlib_renderer._polyCollections, "Mesh not found in renderer"
        #             polyCollections = self._matplotlib_renderer._polyCollections[full_uuid]
        #             mpl_artist = polyCollections
        #             return mpl_artist
        #         else:
        #             assert False, "Visual type not supported yet"
        # assert False, "Visual not found in canvas"
