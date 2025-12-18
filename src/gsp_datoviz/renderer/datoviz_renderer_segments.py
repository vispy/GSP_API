"""Datoviz renderer for Segments visuals."""

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
from gsp.utils.math_utils import MathUtils

from .datoviz_renderer import DatovizRenderer
from ..utils.converter_utils import ConverterUtils


class DatovizRendererSegments:
    """Datoviz renderer for Segments visuals."""
    @staticmethod
    def render(
        renderer: DatovizRenderer,
        viewport: Viewport,
        segments: Segments,
        model_matrix: TransBuf,
        camera: Camera,
    ) -> None:
        """Render Segments visuals using Datoviz.

        Args:
            renderer (DatovizRenderer): The Datoviz renderer instance.
            viewport (Viewport): The viewport to render in.
            segments (Segments): The Segments visual to render.
            model_matrix (TransBuf): The model matrix for the visual.
            camera (Camera): The camera used for rendering.
        """
        dvz_panel = renderer._getOrCreateDvzPanel(viewport)

        # =============================================================================
        # Transform vertices with MVP matrix
        # =============================================================================

        vertices_buffer = TransBufUtils.to_buffer(segments.get_positions())
        model_matrix_buffer = TransBufUtils.to_buffer(model_matrix)
        view_matrix_buffer = TransBufUtils.to_buffer(camera.get_view_matrix())
        projection_matrix_buffer = TransBufUtils.to_buffer(camera.get_projection_matrix())

        # convert all necessary buffers to numpy arrays
        vertices_numpy = Bufferx.to_numpy(vertices_buffer)
        model_matrix_numpy = Bufferx.to_numpy(model_matrix_buffer).squeeze()
        view_matrix_numpy = Bufferx.to_numpy(view_matrix_buffer).squeeze()
        projection_matrix_numpy = Bufferx.to_numpy(projection_matrix_buffer).squeeze()

        # Apply Model-View-Projection transformation to the vertices
        vertices_3d_transformed = MathUtils.apply_mvp_to_vertices(vertices_numpy, model_matrix_numpy, view_matrix_numpy, projection_matrix_numpy)

        # Convert 3D vertices to 3d - shape (N, 3)
        vertices_3d = np.ascontiguousarray(vertices_3d_transformed, dtype=np.float32)

        # =============================================================================
        # Get attributes
        # =============================================================================

        # get attributes from TransBuf to buffer
        colors_buffer = TransBufUtils.to_buffer(segments.get_colors())
        line_widths_buffer = TransBufUtils.to_buffer(segments.get_line_widths())

        # convert buffers to numpy arrays
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
        dvz_initial_vertices = np.ascontiguousarray(vertices_3d[0::2])
        # dvz_vertices_terminal - the odd indices are terminal points
        dvz_terminal_vertices = np.ascontiguousarray(vertices_3d[1::2])
        dvz_initial_cap = ConverterUtils.cap_style_gsp_to_dvz(segments.get_cap_style())
        dvz_terminal_cap = dvz_initial_cap  # same cap for initial and terminal

        dvz_segments.set_position(dvz_initial_vertices, dvz_terminal_vertices)
        dvz_segments.set_color(colors_numpy)
        dvz_segments.set_linewidth(line_widths_px_numpy)
        dvz_segments.set_cap(dvz_initial_cap, dvz_terminal_cap)
