# stdlib imports
import os
from typing import Literal
import typing

# local imports
from gsp.core import Canvas, Viewport
from gsp.types.visual_base import VisualBase
from gsp.core import Camera
from gsp.types.transbuf import TransBuf

from gsp_matplotlib.renderer import MatplotlibRenderer
from gsp_datoviz.renderer import DatovizRenderer
from gsp_network.renderer import NetworkRenderer


class ExampleHelper:

    @staticmethod
    def get_renderer_name() -> Literal["matplotlib", "datoviz", "network"]:
        renderer_name = typing.cast(Literal["matplotlib", "datoviz", "network"], os.environ.get("GSP_RENDERER", "matplotlib"))
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
