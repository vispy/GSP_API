# stdlib imports
import os
from typing import Sequence
import typing

# pip imports
import numpy as np
import datoviz as dvz
from datoviz._panel import Panel as _DvzPanel  # TODO to fix in datoviz ?
from datoviz.visuals import Visual as _DvzVisual
from datoviz.visuals import Pixel as _DvzPixel
from datoviz.visuals import Point as _DvzPoints

# dataviz glossary
# - App: main application
# - Figure: window - GSP Canvas
# - Panel: sub-region in the window - GSP Viewport
# - Visual: visual element - GSP VisualBase

# local imports
from gsp.core.camera import Camera
from gsp.core.canvas import Canvas
from gsp.core.viewport import Viewport
from gsp.core.visual_base import VisualBase
from gsp_matplotlib.extra.bufferx import Bufferx
from gsp.types.transbuf import TransBuf
from gsp.visuals.pixels import Pixels
from gsp.visuals.points import Points
from gsp.visuals.paths import Paths
from gsp.utils.transbuf_utils import TransBufUtils


class DatovizRenderer:
    def __init__(self, canvas: Canvas):
        self._canvas = canvas
        self.dvz_app = dvz.App(background="white")
        self.dvz_figure = self.dvz_app.figure(
            width=canvas.get_width(),
            height=canvas.get_height(),
        )
        self._dvz_panels: dict[str, _DvzPanel] = {}
        """datoviz panel per gsp viewport UUID"""
        self._dvz_visuals: dict[str, _DvzVisual] = {}
        """datoviz visual per gsp visual group UUID"""

        self._group_count: dict[str, int] = {}
        """group count per visual UUID"""

    def get_canvas(self) -> Canvas:
        return self._canvas

    def show(self) -> None:

        # handle non-interactive mode for tests
        inTest = os.environ.get("GSP_INTERACTIVE_MODE") == "False"
        if inTest:
            return

        # listen to keyboard events - if 'q' is pressed, stop the app
        @self.dvz_app.connect(self.dvz_figure)
        def on_keyboard(event):
            # print(f"{event.key_event()} key {event.key()} ({event.key_name()})")
            if event.key_event() == "press" and event.key_name() == "q":
                self.dvz_app.stop()

        # run the datoviz app to show the window
        self.dvz_app.run()

    # =============================================================================
    # .render() function
    # =============================================================================
    def render(
        self,
        viewports: Sequence[Viewport],
        visuals: Sequence[VisualBase],
        model_matrices: Sequence[TransBuf],
        cameras: Sequence[Camera],
        return_image: bool = False,  # NOTE: make False by default. datoviz screenshot can cause segmentation fault in some cases
        image_format: str = "png",
    ) -> bytes:
        # =============================================================================
        # Render all visual
        # =============================================================================

        for viewport, visual, model_matrix, camera in zip(viewports, visuals, model_matrices, cameras):
            self._render_visual(viewport, visual, model_matrix, camera)

        # =============================================================================
        # Return an image if needed
        # =============================================================================

        # FIXME - i got some segmentation fault here when trying to do offscreen rendering with datoviz
        rendered_image = b""
        if return_image:
            assert image_format in ["png"], f"Unsupported image format: {image_format}"
            image_path = "offscreen_python.png"
            self.dvz_app.screenshot(self.dvz_figure, image_path)
            with open(image_path, "rb") as file_reader:
                rendered_image = file_reader.read()

        return rendered_image

    def close(self):
        self.dvz_app.destroy()

    # =============================================================================
    # ._render_pixels()
    # =============================================================================

    def _render_visual(self, viewport: Viewport, visual: VisualBase, model_matrix: TransBuf, camera: Camera) -> None:
        if isinstance(visual, Pixels):
            from .datoviz_renderer_pixels import DatovizRendererPixels

            DatovizRendererPixels.render(self, viewport, visual, model_matrix, camera)
        elif isinstance(visual, Points):
            from .datoviz_renderer_points import DatovizRendererPoints

            DatovizRendererPoints.render(self, viewport, visual, model_matrix, camera)
        elif isinstance(visual, Paths):
            from .datoviz_renderer_paths import DatovizRendererPaths

            DatovizRendererPaths.render(self, viewport, visual, model_matrix, camera)
        else:
            raise NotImplementedError(f"DatovizRenderer.render() does not support visual of type {type(visual)}")

    # =============================================================================
    # Get or create datoviz panel for viewport
    # =============================================================================

    def _getOrCreateDvzPanel(self, viewport: Viewport) -> _DvzPanel:
        viewport_uuid = viewport.get_uuid()
        # if it already exists, return it
        if viewport_uuid in self._dvz_panels:
            return self._dvz_panels[viewport_uuid]

        # create the datoviz panel
        dvz_panel = self.dvz_figure.panel(
            offset=(viewport.get_origin_x(), viewport.get_origin_y()),
            size=(viewport.get_width(), viewport.get_height()),
        )

        # store it
        self._dvz_panels[viewport_uuid] = dvz_panel

        # return newly created panel
        return dvz_panel
