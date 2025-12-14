# stdlib imports
from typing import Sequence
import typing

# pip imports
import numpy as np
from datoviz.visuals import Glyph as _DvzGlyphs

# local imports
from gsp.core.camera import Camera
from gsp.core.viewport import Viewport
from gsp_matplotlib.extra.bufferx import Bufferx
from gsp.types.transbuf import TransBuf
from gsp.visuals.texts import Texts
from gsp.utils.transbuf_utils import TransBufUtils
from .datoviz_renderer import DatovizRenderer
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

        artist_uuid = f"{viewport.get_uuid()}_{texts.get_uuid()}"

        # Create datoviz_visual if they do not exist
        if artist_uuid not in renderer._dvz_visuals:
            artist_uuid = f"{viewport.get_uuid()}_{texts.get_uuid()}"
            dvz_glyphs = renderer._dvz_app.glyph(font_size=30)
            # set dummy strings to initialize the visual
            dvz_glyphs.set_strings(["dummy string"], string_pos=np.array([[0.0, 0.0, 0.0]], dtype=np.float32), scales=np.array([1.0], dtype=np.float32))
            renderer._dvz_visuals[artist_uuid] = dvz_glyphs
            # Add the new visual to the panel
            dvz_panel.add(dvz_glyphs)

        # =============================================================================
        # Update all attributes
        # =============================================================================

        # # get the datoviz visual
        dvz_glyphs = typing.cast(_DvzGlyphs, renderer._dvz_visuals[artist_uuid])

        text_strings = texts.get_strings()
        text_count = len(text_strings)
        glyph_count = sum(map(len, text_strings))

        # build glyph scales from font sizes
        glyph_scales = np.zeros((glyph_count,), dtype=np.float32)
        for text_index in range(text_count):
            # TODO font-size is in typographic points, have to convert to pixels ? relation with the font_size of the dvz visual ?
            # glyph_scales[text_index] = font_sizes_numpy[text_index, 0]  # dvz visual default font size is 100
            for glyph_index in range(len(text_strings[text_index])):
                global_glyph_index = sum(len(s) for s in text_strings[:text_index]) + glyph_index
                glyph_scales[global_glyph_index] = font_sizes_numpy[text_index, 0] / 15  # dvz visual default font size is 100

        # build glyph colors from text colors
        glyph_colors = np.zeros((glyph_count, 4), dtype=np.uint8)
        for text_index in range(text_count):
            for glyph_index in range(len(text_strings[text_index])):
                global_glyph_index = sum(len(s) for s in text_strings[:text_index]) + glyph_index
                glyph_colors[global_glyph_index, :] = colors_numpy[text_index, :]

        glyphs_angles = np.zeros((glyph_count,), dtype=np.float32)
        for text_index in range(text_count):
            for glyph_index in range(len(text_strings[text_index])):
                global_glyph_index = sum(len(s) for s in text_strings[:text_index]) + glyph_index
                glyphs_angles[global_glyph_index] = angles_numpy[text_index, 0] / 180 * np.pi  # convert to radians

        dvz_glyphs.set_strings(text_strings, string_pos=vertices_numpy)
        dvz_glyphs.set_color(glyph_colors)
        dvz_glyphs.set_angle(glyphs_angles)
        dvz_glyphs.set_scale(glyph_scales)
