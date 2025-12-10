# stdlib imports
from typing import Sequence
import typing

# pip imports
import numpy as np
from datoviz.visuals import Point as _DvzPoints

# local imports
from gsp.core.camera import Camera
from gsp.core.canvas import Canvas
from gsp.core.viewport import Viewport
from gsp_matplotlib.extra.bufferx import Bufferx
from gsp.types.transbuf import TransBuf
from gsp.visuals.texts import Texts
from gsp.utils.transbuf_utils import TransBufUtils
from .datoviz_renderer import DatovizRenderer
from gsp.utils.group_utils import GroupUtils
from gsp.utils.unit_utils import UnitUtils


class DatovizRendererTexts:
    @staticmethod
    def render(
        renderer: DatovizRenderer,
        viewport: Viewport,
        texts: Texts,
        model_matrix: TransBuf,
        camera: Camera,
    ) -> None:
        dvz_panel = renderer._getOrCreateDvzPanel(viewport)

        # =============================================================================
        # Get attributes
        # =============================================================================

        # get attributes from TransBuf to buffer
        positions_buffer = TransBufUtils.to_buffer(texts.get_positions())
        colors_buffer = TransBufUtils.to_buffer(texts.get_colors())
        font_sizes_buffer = TransBufUtils.to_buffer(texts.get_font_sizes())
        anchors_buffer = TransBufUtils.to_buffer(texts.get_anchors())
        angles_buffer = TransBufUtils.to_buffer(texts.get_angles())

        # convert buffers to numpy arrays
        vertices_numpy = Bufferx.to_numpy(positions_buffer)
        colors_numpy = Bufferx.to_numpy(colors_buffer)
        font_sizes_numpy = Bufferx.to_numpy(font_sizes_buffer)
        anchors_numpy = Bufferx.to_numpy(anchors_buffer)
        angles_numpy = Bufferx.to_numpy(angles_buffer)

        # =============================================================================
        # Create the datoviz visual if needed
        # =============================================================================

        artist_uuid_sample = f"{viewport.get_uuid()}_{texts.get_uuid()}_0"

        # Create datoviz_visual if they do not exist
        if artist_uuid_sample not in renderer._dvz_visuals:
            for text_index in range(len(texts.get_strings())):
                artist_uuid = f"{viewport.get_uuid()}_{texts.get_uuid()}_{text_index}"
                dvz_points = renderer._dvz_app.point(
                    position=dummy_position_numpy,
                    color=dummy_color_numpy,
                    size=dummy_size_numpy,
                )
                renderer._dvz_visuals[artist_uuid] = dvz_points
                # Add the new visual to the panel
                dvz_panel.add(dvz_points)

        # =============================================================================
        # Update all attributes
        # =============================================================================

        # get the datoviz visual
        dvz_points = typing.cast(_DvzPoints, renderer._dvz_visuals[artist_uuid])

        # set attributes
        group_vertices = vertices_numpy
        dvz_points.set_position(group_vertices)

        # set group_sizes
        group_sizes = np.tile(diameter_px_numpy, group_vertices.__len__()).reshape((-1, 1))
        group_sizes = group_sizes.reshape(-1)  # datoviz expects (N,) shape for (N, 1) input
        dvz_points.set_size(group_sizes)

        # set group_colors
        group_colors = np.tile(face_colors_numpy, group_vertices.__len__()).reshape((-1, 4))
        dvz_points.set_color(group_colors)
