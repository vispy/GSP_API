"""Datoviz renderer for Points visuals."""
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
from gsp.visuals.points import Points
from gsp.utils.transbuf_utils import TransBufUtils
from .datoviz_renderer import DatovizRenderer
from gsp.utils.group_utils import GroupUtils
from gsp.utils.math_utils import MathUtils
from gsp.utils.unit_utils import UnitUtils


class DatovizRendererPoints:
    """Datoviz renderer for Points visuals."""
    @staticmethod
    def render(
        renderer: DatovizRenderer,
        viewport: Viewport,
        points: Points,
        model_matrix: TransBuf,
        camera: Camera,
    ) -> None:
        """Render Points visuals using Datoviz.

        Args:
            renderer (DatovizRenderer): The Datoviz renderer instance.
            viewport (Viewport): The viewport to render in.
            points (Points): The Points visual to render.
            model_matrix (TransBuf): The model matrix for the visual.
            camera (Camera): The camera used for rendering.
        """
        dvz_panel = renderer._getOrCreateDvzPanel(viewport)

        # =============================================================================
        # Transform vertices with MVP matrix
        # =============================================================================

        vertices_buffer = TransBufUtils.to_buffer(points.get_positions())
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
        sizes_buffer = TransBufUtils.to_buffer(points.get_sizes())
        face_colors_buffer = TransBufUtils.to_buffer(points.get_face_colors())

        # convert buffers to numpy arrays
        face_colors_numpy = Bufferx.to_numpy(face_colors_buffer)

        # Convert sizes from point^2 to pixel diameter
        sizes_pt2_numpy = Bufferx.to_numpy(sizes_buffer)
        radius_pt_numpy = np.sqrt(sizes_pt2_numpy / np.pi)
        radius_px_numpy = UnitUtils.point_to_pixel_numpy(radius_pt_numpy, renderer.get_canvas().get_dpi())
        diameter_px_numpy = radius_px_numpy * 2.0 * UnitUtils.device_pixel_ratio()

        # =============================================================================
        # Create the datoviz visual if needed
        # =============================================================================

        artist_uuid = f"{viewport.get_uuid()}_{points.get_uuid()}"

        # Create datoviz_visual if they do not exist
        if artist_uuid not in renderer._dvz_visuals:
            dummy_position_numpy = np.array([[0, 0, 0]], dtype=np.float32).reshape((-1, 3))
            dummy_color_numpy = np.array([[255, 0, 0, 255]], dtype=np.uint8).reshape((-1, 4))
            dummy_size_numpy = np.array([1], dtype=np.float32).reshape((-1, 1)).reshape(-1)
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
        dvz_points.set_position(vertices_3d)

        # set group_sizes
        group_sizes = np.tile(diameter_px_numpy, vertices_3d.__len__()).reshape((-1, 1))
        group_sizes = group_sizes.reshape(-1)  # datoviz expects (N,) shape for (N, 1) input
        dvz_points.set_size(group_sizes)

        # set group_colors
        group_colors = np.tile(face_colors_numpy, vertices_3d.__len__()).reshape((-1, 4))
        dvz_points.set_color(group_colors)
