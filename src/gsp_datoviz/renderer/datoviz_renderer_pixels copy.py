# stdlib imports
from typing import Sequence
import typing

# pip imports
import numpy as np
from datoviz.visuals import Pixel as _DvzPixel

# local imports
from gsp.core.camera import Camera
from gsp.core.canvas import Canvas
from gsp.core.viewport import Viewport
from gsp_matplotlib.extra.bufferx import Bufferx
from gsp.types.transbuf import TransBuf
from gsp.visuals.pixels import Pixels
from gsp.utils.transbuf_utils import TransBufUtils
from .datoviz_renderer import DatovizRenderer


class DatovizRendererPixels:
    @staticmethod
    def render(
        renderer: DatovizRenderer,
        viewport: Viewport,
        visual: Pixels,
        model_matrix: TransBuf,
        camera: Camera,
    ) -> None:
        dvz_panel = renderer._getOrCreateDvzPanel(viewport)

        # =============================================================================
        # Create the datoviz visual if needed
        # =============================================================================

        visual_exists = visual.get_uuid() in renderer.dvz_visuals
        if visual_exists == False:
            dummy_position_numpy = np.array([[0, 0, 0]], dtype=np.float32).reshape((-1, 3))
            dummy_color_numpy = np.array([[255, 0, 0, 255]], dtype=np.uint8).reshape((-1, 4))
            dvz_pixels = renderer.dvz_app.pixel(
                position=dummy_position_numpy,
                color=dummy_color_numpy,
            )
            renderer.dvz_visuals[visual.get_uuid()] = dvz_pixels
            # Add the new visual to the panel
            dvz_panel.add(dvz_pixels)

        # =============================================================================
        # Update all attributes
        # =============================================================================

        # get the datoviz visual
        dvz_pixels = typing.cast(_DvzPixel, renderer.dvz_visuals[visual.get_uuid()])

        # get attributes from TransBuf to numpy
        positions_buffer = TransBufUtils.to_buffer(visual.get_positions())
        colors_buffer = TransBufUtils.to_buffer(visual.get_colors())
        dvz_position_numpy = Bufferx.to_numpy(positions_buffer)
        dvz_color_numpy = Bufferx.to_numpy(colors_buffer)

        # set attributes
        dvz_pixels.set_position(dvz_position_numpy)
        dvz_pixels.set_color(dvz_color_numpy)
