# stdlib imports
from typing import Sequence
import typing

# pip imports
import numpy as np
from datoviz.visuals import Path as _DvzPaths

# local imports
from gsp.core.camera import Camera
from gsp.core.canvas import Canvas
from gsp.core.viewport import Viewport
from gsp_matplotlib.extra.bufferx import Bufferx
from gsp.types.transbuf import TransBuf
from gsp.visuals.paths import Paths
from gsp.utils.transbuf_utils import TransBufUtils
from .datoviz_renderer import DatovizRenderer
from gsp.utils.group_utils import GroupUtils
from gsp.utils.unit_utils import UnitUtils


class DatovizRendererPaths:
    @staticmethod
    def render(
        renderer: DatovizRenderer,
        viewport: Viewport,
        visual: Paths,
        model_matrix: TransBuf,
        camera: Camera,
    ) -> None:
        dvz_panel = renderer._getOrCreateDvzPanel(viewport)
        paths: Paths = visual

        # =============================================================================
        # Get attributes
        # =============================================================================

        # get attributes from TransBuf to buffer
        positions_buffer = TransBufUtils.to_buffer(paths.get_positions())
        path_sizes_buffer = TransBufUtils.to_buffer(paths.get_path_sizes())
        colors_buffer = TransBufUtils.to_buffer(paths.get_colors())
        line_widths_buffer = TransBufUtils.to_buffer(paths.get_line_widths())

        # convert buffers to numpy arrays
        vertices_numpy = Bufferx.to_numpy(positions_buffer)
        path_sizes_numpy = Bufferx.to_numpy(path_sizes_buffer)
        colors_numpy = Bufferx.to_numpy(colors_buffer)
        line_widths_pt_numpy = Bufferx.to_numpy(line_widths_buffer)

        # Convert sizes from point^2 to pixel diameter
        line_widths_px_numpy = UnitUtils.point_to_pixel_numpy(line_widths_pt_numpy, renderer.get_canvas().get_dpi())

        path_sizes_numpy = path_sizes_numpy.reshape(-1)  # datoviz expects (N,) shape for (N, 1) input
        line_widths_px_numpy = line_widths_px_numpy.reshape(-1)  # datoviz expects (N,) shape for (N, 1) input

        # =============================================================================
        # Create the datoviz visual if needed
        # =============================================================================

        # Create datoviz_visual if they do not exist
        if visual.get_uuid() not in renderer._dvz_visuals:
            dummy_position_numpy = np.array([[0, 0, 0]], dtype=np.float32).reshape((-1, 3))
            dummy_path_sizes_numpy = np.array([1], dtype=np.uint32)
            dvz_paths = renderer.dvz_app.path()
            dvz_paths.set_position(dummy_position_numpy, groups=dummy_path_sizes_numpy)
            renderer._dvz_visuals[visual.get_uuid()] = dvz_paths
            # Add the new visual to the panel
            dvz_panel.add(dvz_paths)

        # =============================================================================
        # Update all attributes
        # =============================================================================

        # get the datoviz visual
        dvz_paths = typing.cast(_DvzPaths, renderer._dvz_visuals[visual.get_uuid()])

        dvz_paths.set_position(vertices_numpy, groups=path_sizes_numpy)
        dvz_paths.set_color(colors_numpy)
        dvz_paths.set_linewidth(line_widths_px_numpy)
