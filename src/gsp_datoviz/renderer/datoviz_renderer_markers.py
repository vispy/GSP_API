# stdlib imports
from typing import Sequence
import typing

# pip imports
import numpy as np
from datoviz.visuals import Marker as _DvzMarkers

# local imports
from gsp.core.camera import Camera
from gsp.core.canvas import Canvas
from gsp.core.viewport import Viewport
from gsp_matplotlib.extra.bufferx import Bufferx
from gsp.types.transbuf import TransBuf
from gsp.visuals.markers import Markers
from gsp.utils.transbuf_utils import TransBufUtils
from .datoviz_renderer import DatovizRenderer
from gsp.utils.group_utils import GroupUtils
from gsp.utils.unit_utils import UnitUtils


class DatovizRendererMarkers:
    @staticmethod
    def render(
        renderer: DatovizRenderer,
        viewport: Viewport,
        markers: Markers,
        model_matrix: TransBuf,
        camera: Camera,
    ) -> None:
        dvz_panel = renderer._getOrCreateDvzPanel(viewport)

        # =============================================================================
        # Get attributes
        # =============================================================================

        # =============================================================================
        # Convert all attributes to numpy arrays
        # =============================================================================

        positions_buffer = TransBufUtils.to_buffer(markers.get_positions())
        sizes_buffer = TransBufUtils.to_buffer(markers.get_sizes())
        face_colors_buffer = TransBufUtils.to_buffer(markers.get_face_colors())
        edge_colors_buffer = TransBufUtils.to_buffer(markers.get_edge_colors())
        edge_widths_buffer = TransBufUtils.to_buffer(markers.get_edge_widths())

        # Convert buffers to numpy arrays)
        positions_numpy = Bufferx.to_numpy(positions_buffer)
        face_colors_numpy = Bufferx.to_numpy(face_colors_buffer)
        edge_colors_numpy = Bufferx.to_numpy(edge_colors_buffer)

        sizes_pt_numpy = Bufferx.to_numpy(sizes_buffer).reshape(-1)
        sizes_px_numpy = UnitUtils.point_to_pixel_numpy(sizes_pt_numpy, renderer.get_canvas().get_dpi())
        sizes_px_numpy = sizes_px_numpy.reshape(-1)

        edge_widths_pt_numpy = Bufferx.to_numpy(edge_widths_buffer)
        edge_widths_px_numpy = UnitUtils.point_to_pixel_numpy(edge_widths_pt_numpy, renderer.get_canvas().get_dpi())
        edge_widths_px_numpy = edge_widths_px_numpy.reshape(-1)

        # =============================================================================
        # Create the datoviz visual if needed
        # =============================================================================

        # Create datoviz_visual if they do not exist
        if markers.get_uuid() not in renderer._dvz_visuals:
            dummy_position_numpy = np.array([[0, 0, 0]], dtype=np.float32).reshape((-1, 3))
            dvz_markers = renderer.dvz_app.marker(position=dummy_position_numpy)
            renderer._dvz_visuals[markers.get_uuid()] = dvz_markers
            # Add the new visual to the panel
            dvz_panel.add(dvz_markers)

        # =============================================================================
        # Update all attributes
        # =============================================================================

        # get the datoviz visual
        dvz_markers = typing.cast(_DvzMarkers, renderer._dvz_visuals[markers.get_uuid()])

        # set attributes
        dvz_markers.set_position(positions_numpy)

        dvz_markers.set_size(sizes_px_numpy)
        dvz_markers.set_color(face_colors_numpy)
        dvz_markers.set_linewidth(edge_widths_px_numpy[0])
        # dvz_markers.set_edgecolor(edge_colors_numpy[0].tolist())  # datoviz only supports a single edge color

        dvz_markers.set_mode("code")
        dvz_markers.set_aspect("filled")
        dvz_markers.set_shape("club")
