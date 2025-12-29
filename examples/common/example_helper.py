"""Helper class for examples to create renderers and animators based on environment variables."""

# stdlib imports
import os
from typing import Literal
import typing
import pathlib

# local imports
from gsp.core import Canvas, Viewport
from gsp.types.visual_base import VisualBase
from gsp.core import Camera
from gsp.types.transbuf import TransBuf


from gsp.types.renderer_base import RendererBase
from gsp_matplotlib.renderer import MatplotlibRenderer
from gsp_datoviz.renderer import DatovizRenderer
from gsp_network.renderer import NetworkRenderer

from gsp_extra.animator.animator_base import AnimatorBase
from gsp_extra.animator.animator_datoviz import AnimatorDatoviz
from gsp_extra.animator.animator_matplotlib import AnimatorMatplotlib
from gsp_extra.animator.animator_network import AnimatorNetwork

from gsp_extra.viewport_events.viewport_events_base import ViewportEventsBase
from gsp_extra.viewport_events.viewport_events_matplotlib import ViewportEventsMatplotlib
from gsp_extra.viewport_events.viewport_events_datoviz import ViewportEventsDatoviz
from gsp_extra.viewport_events.viewport_events_network import ViewportEventsNetwork


class ExampleHelper:
    """Helper class for examples to create renderers and animators based on environment variables."""

    default_renderer_name: Literal["matplotlib", "datoviz", "network"] = "matplotlib"
    # default_renderer_name: Literal["matplotlib", "datoviz", "network"] = "datoviz"

    @staticmethod
    def get_renderer_name() -> Literal["matplotlib", "datoviz", "network"]:
        """Get the renderer name from environment variable GSP_RENDERER."""
        renderer_name = typing.cast(Literal["matplotlib", "datoviz", "network"], os.environ.get("GSP_RENDERER", ExampleHelper.default_renderer_name))
        # sanity check - ensure renderer_name is one of the expected valueszx
        assert renderer_name in ["matplotlib", "datoviz", "network"], f"Invalid renderer name: {renderer_name}"
        return typing.cast(Literal["matplotlib", "datoviz", "network"], renderer_name)

    @staticmethod
    def get_remote_renderer_name() -> Literal["matplotlib", "datoviz"]:
        """Get the remote renderer name from environment variable GSP_REMOTE_RENDERER. Valid iif renderer is 'network'."""
        remote_renderer_name = typing.cast(Literal["matplotlib", "datoviz"], os.environ.get("GSP_REMOTE_RENDERER", "matplotlib"))
        # sanity check - ensure renderer_name is one of the expected values
        assert remote_renderer_name in ["matplotlib", "datoviz"], f"Invalid remote renderer name: {remote_renderer_name}"
        return typing.cast(Literal["matplotlib", "datoviz"], remote_renderer_name)

    @staticmethod
    def create_renderer(renderer_name: Literal["matplotlib", "datoviz", "network"], canvas: Canvas) -> RendererBase:
        """Create a renderer based on the given renderer name.

        Args:
            renderer_name (Literal["matplotlib", "datoviz", "network"]): Name of the renderer to create.
            canvas (Canvas): The canvas to associate with the renderer.

        Returns:
            RendererBase: The created renderer instance.
        """
        if renderer_name == "matplotlib":
            return MatplotlibRenderer(canvas)
        elif renderer_name == "datoviz":
            return DatovizRenderer(canvas)
        elif renderer_name == "network":
            remote_renderer_name = ExampleHelper.get_remote_renderer_name()
            return NetworkRenderer(canvas, "http://localhost:5000", remote_renderer_name)
        else:
            raise ValueError(f"Unknown renderer name: {renderer_name}")

    # =============================================================================
    #
    # =============================================================================

    @staticmethod
    def create_animator(renderer: RendererBase) -> AnimatorBase:
        """Create an animator based on the given renderer.

        Args:
            renderer (RendererBase): The renderer to associate with the animator.

        Returns:
            AnimatorBase: The created animator instance.
        """
        # init the animator with the renderer
        if isinstance(renderer, MatplotlibRenderer):
            animator = AnimatorMatplotlib(typing.cast(MatplotlibRenderer, renderer))
        elif isinstance(renderer, DatovizRenderer):
            animator = AnimatorDatoviz(typing.cast(DatovizRenderer, renderer))
        elif isinstance(renderer, NetworkRenderer):
            animator = AnimatorNetwork(typing.cast(NetworkRenderer, renderer))
        else:
            raise NotImplementedError(f"Animator for renderer {renderer} is not implemented in this example.")
        return animator

    @staticmethod
    def create_animator_with_video(renderer: RendererBase, video_path: str, fps: int, video_duration: float) -> AnimatorBase:
        """Create an animator with video saving based on the given renderer.

        Args:
            renderer (RendererBase): The renderer to associate with the animator.
            video_path (str): Path to save the video.
            fps (int): Frames per second for the video.
            video_duration (float): Duration of the video in seconds.

        Returns:
            AnimatorBase: The created animator instance.
        """
        # init the animator with the renderer
        if isinstance(renderer, MatplotlibRenderer):
            animator = AnimatorMatplotlib(typing.cast(MatplotlibRenderer, renderer), fps=fps, video_duration=video_duration, video_path=video_path)
        elif isinstance(renderer, DatovizRenderer):
            animator = AnimatorDatoviz(typing.cast(DatovizRenderer, renderer), fps=fps, video_duration=video_duration, video_path=video_path)
        elif isinstance(renderer, NetworkRenderer):
            animator = AnimatorNetwork(typing.cast(NetworkRenderer, renderer), fps=fps, video_duration=video_duration, video_path=video_path)
        else:
            raise NotImplementedError(f"Animator for renderer {renderer} is not implemented in this example.")
        return animator

    # =============================================================================
    #
    # =============================================================================

    @staticmethod
    def create_viewport_events(renderer: RendererBase, viewport: Viewport) -> ViewportEventsBase:
        """Create ViewportEvents based on the given renderer and viewport.

        Args:
            renderer (RendererBase): The renderer associated with the viewport.
            viewport (Viewport): The viewport to create events for.

        Returns:
            ViewportEventsBase: The created ViewportEvents instance.
        """
        if isinstance(renderer, MatplotlibRenderer):
            return ViewportEventsMatplotlib(typing.cast(MatplotlibRenderer, renderer), viewport)
        elif isinstance(renderer, DatovizRenderer):
            return ViewportEventsDatoviz(typing.cast(DatovizRenderer, renderer), viewport)
        elif isinstance(renderer, NetworkRenderer):
            return ViewportEventsNetwork(typing.cast(NetworkRenderer, renderer), viewport)
        else:
            raise NotImplementedError(f"Viewport events for renderer {renderer} is not implemented in this example.")

    # =============================================================================
    #
    # =============================================================================

    @staticmethod
    def save_output_image(rendered_image: bytes, image_basename: str) -> None:
        """Save rendered image to output path.

        Args:
            rendered_image (bytes): The rendered image data.
            image_basename (str): The basename for the output image file.
        """
        image_path = pathlib.Path(__file__).parent / ".." / "output" / image_basename
        with open(image_path, "wb") as file_writer:
            file_writer.write(rendered_image)
        print(f"Rendered image saved to: {image_path}")
