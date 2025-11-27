# stdlib imports
import os
from typing import Literal
import typing

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

    default_renderer_name: Literal["matplotlib", "datoviz", "network"] = "matplotlib"

    @staticmethod
    def get_renderer_name() -> Literal["matplotlib", "datoviz", "network"]:
        renderer_name = typing.cast(Literal["matplotlib", "datoviz", "network"], os.environ.get("GSP_RENDERER", ExampleHelper.default_renderer_name))
        # sanity check - ensure renderer_name is one of the expected valueszx
        assert renderer_name in ["matplotlib", "datoviz", "network"], f"Invalid renderer name: {renderer_name}"
        return typing.cast(Literal["matplotlib", "datoviz", "network"], renderer_name)

    @staticmethod
    def get_remote_renderer_name() -> Literal["matplotlib", "datoviz"]:
        """Get the remote renderer name from environment variable GSP_REMOTE_RENDERER. Valid iif renderer is 'network'"""
        remote_renderer_name = typing.cast(Literal["matplotlib", "datoviz"], os.environ.get("GSP_REMOTE_RENDERER", "matplotlib"))
        # sanity check - ensure renderer_name is one of the expected values
        assert remote_renderer_name in ["matplotlib", "datoviz"], f"Invalid remote renderer name: {remote_renderer_name}"
        return typing.cast(Literal["matplotlib", "datoviz"], remote_renderer_name)

    @staticmethod
    def create_renderer(renderer_name: Literal["matplotlib", "datoviz", "network"], canvas: Canvas):
        if renderer_name == "matplotlib":
            return MatplotlibRenderer(canvas)
        elif renderer_name == "datoviz":
            return DatovizRenderer(canvas)
        elif renderer_name == "network":
            remote_renderer_name = ExampleHelper.get_remote_renderer_name()
            return NetworkRenderer(canvas, "http://localhost:5000", remote_renderer_name)
        else:
            raise ValueError(f"Unknown renderer name: {renderer_name}")

    @staticmethod
    def render_and_show(
        canvas: Canvas,
        viewports: list[Viewport],
        visuals: list[VisualBase],
        model_matrices: list[TransBuf],
        cameras: list[Camera],
        /,
        renderer_name: Literal["matplotlib", "datoviz", "network"] | None = None,
    ):
        if renderer_name is None:
            renderer_name = ExampleHelper.get_renderer_name()
        # Create a renderer
        renderer = ExampleHelper.create_renderer(renderer_name, canvas)
        # render the scene
        renderer.render(viewports, visuals, model_matrices, cameras)
        # show the rendered scene
        renderer.show()

    # =============================================================================
    #
    # =============================================================================

    @staticmethod
    def create_animator(renderer: RendererBase) -> AnimatorBase:
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
    def create_animator_with_video(
        renderer: RendererBase,
        video_path: str,
        fps: int,
        video_duration: float,
    ) -> AnimatorBase:
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
        if isinstance(renderer, MatplotlibRenderer):
            return ViewportEventsMatplotlib(typing.cast(MatplotlibRenderer, renderer), viewport)
        elif isinstance(renderer, DatovizRenderer):
            return ViewportEventsDatoviz(typing.cast(DatovizRenderer, renderer), viewport)
        elif isinstance(renderer, NetworkRenderer):
            return ViewportEventsNetwork(typing.cast(NetworkRenderer, renderer), viewport)
        else:
            raise NotImplementedError(f"Viewport events for renderer {renderer} is not implemented in this example.")
