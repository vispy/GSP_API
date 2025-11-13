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
from gsp.utils.group_utils import GroupUtils


class DatovizRendererPixels:
    @staticmethod
    def render(
        renderer: DatovizRenderer,
        viewport: Viewport,
        pixels: Pixels,
        model_matrix: TransBuf,
        camera: Camera,
    ) -> None:
        dvz_panel = renderer._getOrCreateDvzPanel(viewport)

        # =============================================================================
        # Get attributes
        # =============================================================================

        # get attributes from TransBuf to buffer
        positions_buffer = TransBufUtils.to_buffer(pixels.get_positions())
        colors_buffer = TransBufUtils.to_buffer(pixels.get_colors())

        # convert buffers to numpy arrays
        vertices_numpy = Bufferx.to_numpy(positions_buffer)
        colors_numpy = Bufferx.to_numpy(colors_buffer)

        # =============================================================================
        #   Compute indices_per_group for groups depending on the type of groups
        # =============================================================================

        indices_per_group = GroupUtils.compute_indices_per_group(vertices_numpy.__len__(), pixels.get_groups())
        group_count = GroupUtils.get_group_count(vertices_numpy.__len__(), pixels.get_groups())

        # =============================================================================
        # Create the datoviz pixels if needed
        # =============================================================================

        # update stored group count
        old_group_count = None
        if pixels.get_uuid() in renderer._group_count:
            old_group_count = renderer._group_count[pixels.get_uuid()]
        renderer._group_count[pixels.get_uuid()] = group_count

        # If the group count has changed, destroy old datoviz_visuals
        if old_group_count is not None and old_group_count != group_count:
            for group_index in range(old_group_count):
                group_uuid = f"{pixels.get_uuid()}_group_{group_index}"
                if group_uuid in renderer._dvz_visuals:
                    dvz_pixels = typing.cast(_DvzPixel, renderer._dvz_visuals[group_uuid])
                    dvz_panel.remove(dvz_pixels)
                    del renderer._dvz_visuals[group_uuid]

        # Create datoviz_visual if they do not exist
        sample_group_uuid = f"{pixels.get_uuid()}_group_0"
        if sample_group_uuid not in renderer._dvz_visuals:
            for group_index in range(group_count):
                dummy_position_numpy = np.array([[0, 0, 0]], dtype=np.float32).reshape((-1, 3))
                dummy_color_numpy = np.array([[255, 0, 0, 255]], dtype=np.uint8).reshape((-1, 4))
                dvz_pixels = renderer.dvz_app.pixel(
                    position=dummy_position_numpy,
                    color=dummy_color_numpy,
                )
                group_uuid = f"{pixels.get_uuid()}_group_{group_index}"
                renderer._dvz_visuals[group_uuid] = dvz_pixels
                # Add the new pixels to the panel
                dvz_panel.add(dvz_pixels)

        # =============================================================================
        # Update all attributes
        # =============================================================================

        for group_index in range(group_count):
            group_uuid = f"{pixels.get_uuid()}_group_{group_index}"

            # get the datoviz pixels
            dvz_pixels = typing.cast(_DvzPixel, renderer._dvz_visuals[group_uuid])

            # set attributes
            group_vertices = vertices_numpy[indices_per_group[group_index]]
            dvz_pixels.set_position(group_vertices)

            # set group_colors
            group_colors = np.tile(colors_numpy[group_index], group_vertices.__len__()).reshape((-1, 4))
            dvz_pixels.set_color(group_colors)
