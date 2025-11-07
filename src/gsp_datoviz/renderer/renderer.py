# stdlib imports
from typing import Sequence
import typing

# pip imports
import numpy as np
import datoviz as dvz
from datoviz._panel import Panel as _DvzPanel  # TODO to fix in datoviz ?
from datoviz.visuals import Visual as _DvzVisual
from datoviz.visuals import Pixel as _DvzPixel

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
from gsp.utils.transbuf_utils import TransBufUtils


class DatovizRenderer:
    def __init__(self, canvas: Canvas):
        self.dvz_app = dvz.App(background="white")
        self.dvz_figure = self.dvz_app.figure(
            width=canvas.get_width(),
            height=canvas.get_height(),
        )
        self.dvz_panels: dict[str, _DvzPanel] = {}
        """datoviz panel per gsp viewport UUID"""
        self.dvz_visuals: dict[str, _DvzVisual] = {}
        """datoviz visual per gsp visual UUID"""

    def render(
        self,
        viewports: Sequence[Viewport],
        visuals: Sequence[VisualBase],
        model_matrices: Sequence[TransBuf],
        cameras: Sequence[Camera],
        return_image: bool = True,
        image_format: str = "png",
    ) -> bytes:
        for viewport, visual, model_matrix, camera in zip(viewports, visuals, model_matrices, cameras):
            if isinstance(visual, Pixels):
                self._render_pixels(viewport, visual, model_matrix, camera)

        #

        # =============================================================================
        # Return an image if needed
        # =============================================================================

        # FIXME - i dunno how to generate image from datoviz
        rendered_image = b""
        if return_image:
            assert image_format in ["png"], f"Unsupported image format: {image_format}"
            self.dvz_app.run(1)

        return rendered_image

    def close(self):
        self.dvz_app.destroy()

    # =============================================================================
    #
    # =============================================================================

    def _render_pixels(self, viewport: Viewport, visual: Pixels, model_matrix: TransBuf, camera: Camera) -> None:
        dvz_panel = self._getOrCreateDvzPanel(viewport)

        # =============================================================================
        # Create the datoviz visual if needed
        # =============================================================================

        visual_exists = visual.get_uuid() in self.dvz_visuals
        if visual_exists == False:
            dvz_position_numpy = np.array([[0, 0, 0]], dtype=np.float32).reshape((-1, 3))
            dvz_color_numpy = np.array([[255, 0, 0, 255]], dtype=np.uint8).reshape((-1, 4))
            dvz_pixels = self.dvz_app.pixel(
                position=dvz_position_numpy,
                color=dvz_color_numpy,
            )
            self.dvz_visuals[visual.get_uuid()] = dvz_pixels
            # Add the new visual to the panel
            dvz_panel.add(dvz_pixels)

        # =============================================================================
        # Update all attributes
        # =============================================================================

        # get the datoviz visual
        dvz_pixels = typing.cast(_DvzPixel, self.dvz_visuals[visual.get_uuid()])

        # get attributes from TransBuf to numpy
        positions_buffer = TransBufUtils.to_buffer(visual.get_positions())
        colors_buffer = TransBufUtils.to_buffer(visual.get_colors())
        dvz_position_numpy = Bufferx.to_numpy(positions_buffer)
        dvz_color_numpy = Bufferx.to_numpy(colors_buffer)

        # set attributes
        dvz_pixels.set_position(dvz_position_numpy)
        dvz_pixels.set_color(dvz_color_numpy)

    # =============================================================================
    #
    # =============================================================================

    def _getOrCreateDvzPanel(self, viewport: Viewport) -> _DvzPanel:
        viewport_uuid = viewport.get_uuid()
        if viewport_uuid in self.dvz_panels:
            return self.dvz_panels[viewport_uuid]

        dvz_panel = self.dvz_figure.panel()
        self.dvz_panels[viewport_uuid] = dvz_panel

        return dvz_panel
