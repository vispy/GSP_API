# stdlib imports
from typing import Sequence

# pip imports
import datoviz as dvz
from datoviz._panel import Panel as _DvzPanel  # TODO to fix in datoviz ?

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
        self.dvz_visuals: dict[str, dvz.DvzVisual] = {}
        """datoviz visual per gsp visual UUID"""

    def render(
        self,
        viewports: Sequence[Viewport],
        visuals: Sequence[VisualBase],
        model_matrices: Sequence[TransBuf],
        cameras: Sequence[Camera],
        image_format: str = "png",
    ):
        for viewport, visual, model_matrix, camera in zip(viewports, visuals, model_matrices, cameras):
            dvz_panel = self._getOrCreateDvzPanel(viewport)

            if isinstance(visual, Pixels):
                positions_buffer = TransBufUtils.to_buffer(visual.get_positions())
                colors_buffer = TransBufUtils.to_buffer(visual.get_colors())
                dvz_position_numpy = Bufferx.to_numpy(positions_buffer)
                dvz_color_numpy = Bufferx.to_numpy(colors_buffer)

                dvz_visual = self.dvz_app.pixel(
                    position=dvz_position_numpy,
                    color=dvz_color_numpy,
                )
                dvz_panel.add(dvz_visual)

        self.dvz_app.run()

        # FIXME - i dunno how to generate image from datoviz
        generated_image = b""

        return generated_image

    def close(self):
        self.dvz_app.destroy()

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
