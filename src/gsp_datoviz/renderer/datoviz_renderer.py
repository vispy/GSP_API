# stdlib imports
import os
from typing import Sequence
import pathlib
import warnings

# pip imports
import numpy as np
import datoviz as dvz
from datoviz._panel import Panel as _DvzPanel  # TODO _panel to fix in datoviz ?
from datoviz._figure import Figure as _DvzFigure
from datoviz.visuals import Visual as _DvzVisual

# dataviz glossary
# - App: main application
# - Figure: window - GSP Canvas
# - Panel: sub-region in the window - GSP Viewport
# - Visual: visual element - GSP VisualBase

# local imports
from gsp.core.camera import Camera
from gsp.core.canvas import Canvas
from gsp.core.viewport import Viewport
from gsp.types.visual_base import VisualBase
from gsp.types.transbuf import TransBuf
from gsp.visuals.markers import Markers
from gsp.visuals.pixels import Pixels
from gsp.visuals.points import Points
from gsp.visuals.paths import Paths
from gsp.visuals.segments import Segments
from gsp.types.renderer_base import RendererBase


class DatovizRenderer(RendererBase):
    def __init__(self, canvas: Canvas, offscreen: bool = False) -> None:
        self._canvas = canvas
        self._dvz_app: dvz.App = dvz.App(background="white", offscreen=offscreen)
        self._dvz_figure: _DvzFigure = self._dvz_app.figure(
            width=canvas.get_width(),
            height=canvas.get_height(),
        )
        self._dvz_panels: dict[str, _DvzPanel] = {}
        """datoviz panel per gsp viewport UUID"""
        self._dvz_visuals: dict[str, _DvzVisual] = {}
        """datoviz visual per gsp visual group UUID"""

        self._group_count: dict[str, int] = {}
        """group count per visual UUID"""

    def close(self) -> None:
        self._dvz_app.destroy()

    def get_canvas(self) -> Canvas:
        return self._canvas

    def get_dvz_app(self) -> dvz.App:
        return self._dvz_app

    def get_dvz_figure(self) -> _DvzFigure:
        return self._dvz_figure

    def show(self) -> None:

        # handle non-interactive mode for tests
        inTest = os.environ.get("GSP_INTERACTIVE_MODE") == "False"
        if inTest:
            return

        # listen to keyboard events - if 'q' is pressed, stop the app
        @self._dvz_app.connect(self._dvz_figure)
        def on_keyboard(event):
            # print(f"{event.key_event()} key {event.key()} ({event.key_name()})")
            if event.key_event() == "press" and event.key_name() == "q":
                self._dvz_app.stop()

        # run the datoviz app to show the window
        self._dvz_app.run()

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

        # sanity check
        has_offscreen = bool(self._dvz_app.c_flags | dvz.APP_FLAGS_OFFSCREEN)
        if return_image and not has_offscreen:
            raise Exception("DatovizRenderer.render(): cannot return image when datoviz App is not in offscreen mode")

        rendered_image = b""
        if return_image:
            assert image_format in ["png"], f"Unsupported image format: {image_format}"
            image_path = pathlib.Path(__file__).parent / "_datoviz_offscreen_python.png"
            self._dvz_app.screenshot(self._dvz_figure, str(image_path))
            with open(image_path, "rb") as file_reader:
                rendered_image = file_reader.read()
            image_path.unlink()

        return rendered_image

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
        elif isinstance(visual, Markers):
            from .datoviz_renderer_markers import DatovizRendererMarkers

            DatovizRendererMarkers.render(self, viewport, visual, model_matrix, camera)
        elif isinstance(visual, Segments):
            from .datoviz_renderer_segments import DatovizRendererSegments

            DatovizRendererSegments.render(self, viewport, visual, model_matrix, camera)
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
        dvz_panel = self._dvz_figure.panel(
            offset=(viewport.get_x(), viewport.get_y()),
            size=(viewport.get_width(), viewport.get_height()),
        )

        # store it
        self._dvz_panels[viewport_uuid] = dvz_panel

        # return newly created panel
        return dvz_panel
