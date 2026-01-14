"""Datoviz renderer for Paths visuals."""

# stdlib imports
import typing

# pip imports
import numpy as np
from datoviz.visuals import Path as _DvzPaths

# local imports
from gsp.core.camera import Camera
from gsp.core.viewport import Viewport
from gsp_matplotlib.extra.bufferx import Bufferx
from gsp.types.transbuf import TransBuf
from gsp.visuals.paths import Paths
from gsp.utils.transbuf_utils import TransBufUtils
from gsp.utils.unit_utils import UnitUtils
from gsp.utils.math_utils import MathUtils
from .datoviz_renderer import DatovizRenderer
from ..utils.converter_utils import ConverterUtils


class DatovizRendererPaths:
    """Datoviz renderer for Paths visuals."""

    @staticmethod
    def render(
        renderer: DatovizRenderer,
        viewport: Viewport,
        paths: Paths,
        model_matrix: TransBuf,
        camera: Camera,
    ) -> None:
        """Render Paths visuals using Datoviz.

        Args:
            renderer (DatovizRenderer): The Datoviz renderer instance.
            viewport (Viewport): The viewport to render in.
            paths (Paths): The Paths visual to render.
            model_matrix (TransBuf): The model matrix for the visual.
            camera (Camera): The camera used for rendering.
        """
        dvz_panel = renderer._getOrCreateDvzPanel(viewport)
        # =============================================================================
        # Transform vertices with MVP matrix
        # =============================================================================

        vertices_buffer = TransBufUtils.to_buffer(paths.get_positions())
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
        path_sizes_buffer = TransBufUtils.to_buffer(paths.get_path_sizes())
        colors_buffer = TransBufUtils.to_buffer(paths.get_colors())
        line_widths_buffer = TransBufUtils.to_buffer(paths.get_line_widths())

        # convert buffers to numpy arrays
        path_sizes_numpy = Bufferx.to_numpy(path_sizes_buffer)
        colors_numpy = Bufferx.to_numpy(colors_buffer)
        line_widths_pt_numpy = Bufferx.to_numpy(line_widths_buffer)

        # Convert sizes from point^2 to pixel diameter
        line_widths_px_numpy = UnitUtils.point_to_pixel_numpy(line_widths_pt_numpy, renderer.get_canvas().get_dpi())

        path_sizes_numpy = path_sizes_numpy.reshape(-1)  # datoviz expects (N,) shape for (N, 1) input
        line_widths_px_numpy = line_widths_px_numpy.reshape(-1)  # datoviz expects (N,) shape for (N, 1) input

        # =============================================================================
        # Sanity checks attributes buffers
        # =============================================================================

        Paths.sanity_check_attributes_buffer(
            vertices_buffer,
            path_sizes_buffer,
            colors_buffer,
            line_widths_buffer,
            paths.get_cap_style(),
            paths.get_join_style(),
        )

        # =============================================================================
        # Create the datoviz visual if needed
        # =============================================================================

        artist_uuid = f"{viewport.get_uuid()}_{paths.get_uuid()}"

        # Create datoviz_visual if they do not exist
        if artist_uuid not in renderer._dvz_visuals:
            dummy_position_numpy = np.array([[0, 0, 0]], dtype=np.float32).reshape((-1, 3))
            dummy_path_sizes_numpy = np.array([1], dtype=np.uint32)
            dvz_paths = renderer._dvz_app.path()
            dvz_paths.set_position(dummy_position_numpy, groups=dummy_path_sizes_numpy)
            renderer._dvz_visuals[artist_uuid] = dvz_paths
            # Add the new visual to the panel
            dvz_panel.add(dvz_paths)

        # =============================================================================
        # Update all attributes
        # =============================================================================

        # get the datoviz visual
        dvz_paths = typing.cast(_DvzPaths, renderer._dvz_visuals[artist_uuid])

        dvz_paths.set_position(vertices_3d, groups=path_sizes_numpy)
        dvz_paths.set_color(colors_numpy)
        dvz_paths.set_linewidth(line_widths_px_numpy)
        dvz_paths.set_cap(ConverterUtils.cap_style_gsp_to_dvz(paths.get_cap_style()))
        dvz_paths.set_join(ConverterUtils.join_style_gsp_to_dvz(paths.get_join_style()))
