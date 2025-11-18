# stdlib imports
from typing import Sequence
import typing

# pip imports
import numpy as np
from datoviz.visuals import Segment as _DvzSegments

# local imports
from gsp.core.camera import Camera
from gsp.core.canvas import Canvas
from gsp.core.viewport import Viewport
from gsp_matplotlib.extra.bufferx import Bufferx
from gsp.types.transbuf import TransBuf
from gsp.visuals.segments import Segments
from gsp.utils.transbuf_utils import TransBufUtils
from gsp.utils.unit_utils import UnitUtils

from .datoviz_renderer import DatovizRenderer
from ..utils.converter_utils import ConverterUtils


class DatovizRendererSegments:
    @staticmethod
    def render(
        renderer: DatovizRenderer,
        viewport: Viewport,
        segments: Segments,
        model_matrix: TransBuf,
        camera: Camera,
    ) -> None:
        dvz_panel = renderer._getOrCreateDvzPanel(viewport)

        # =============================================================================
        # Get attributes
        # =============================================================================

        # get attributes from TransBuf to buffer
        positions_buffer = TransBufUtils.to_buffer(segments.get_positions())
        colors_buffer = TransBufUtils.to_buffer(segments.get_colors())
        line_widths_buffer = TransBufUtils.to_buffer(segments.get_line_widths())

        # convert buffers to numpy arrays
        vertices_numpy = Bufferx.to_numpy(positions_buffer)
        colors_numpy = Bufferx.to_numpy(colors_buffer)
        line_widths_pt_numpy = Bufferx.to_numpy(line_widths_buffer)

        # Convert sizes from point to pixel diameter
        line_widths_px_numpy = UnitUtils.point_to_pixel_numpy(line_widths_pt_numpy, renderer.get_canvas().get_dpi())
        line_widths_px_numpy = line_widths_px_numpy.reshape(-1)  # datoviz expects (N,) shape for (N, 1) input

        # =============================================================================
        # Create the datoviz visual if needed
        # =============================================================================

        artist_uuid = f"{viewport.get_uuid()}_{segments.get_uuid()}"

        # Create datoviz_visual if they do not exist
        if artist_uuid not in renderer._dvz_visuals:
            dummy_position_numpy = np.array([[0, 0, 0]], dtype=np.float32).reshape((-1, 3))
            dvz_segments = renderer._dvz_app.segment(dummy_position_numpy, dummy_position_numpy)
            renderer._dvz_visuals[artist_uuid] = dvz_segments
            # Add the new visual to the panel
            dvz_panel.add(dvz_segments)

        # =============================================================================
        # Update all attributes
        # =============================================================================

        # get the datoviz visual
        dvz_segments = typing.cast(_DvzSegments, renderer._dvz_visuals[artist_uuid])

        # dvz_vertices_initial - the even indices are initial points
        dvz_initial_vertices = np.ascontiguousarray(vertices_numpy[0::2])
        # dvz_vertices_terminal - the odd indices are terminal points
        dvz_terminal_vertices = np.ascontiguousarray(vertices_numpy[1::2])
        dvz_initial_cap = ConverterUtils.cap_style_gsp_to_dvz(segments.get_cap_style())
        dvz_terminal_cap = dvz_initial_cap  # same cap for initial and terminal

        dvz_segments.set_position(dvz_initial_vertices, dvz_terminal_vertices)
        dvz_segments.set_color(colors_numpy)
        dvz_segments.set_linewidth(line_widths_px_numpy)
        dvz_segments.set_cap(dvz_initial_cap, dvz_terminal_cap)
