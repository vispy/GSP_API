""""Datoviz renderer for Markers visuals."""

# stdlib imports
import typing
import warnings

# pip imports
import numpy as np
from datoviz.visuals import Marker as _DvzMarkers

# local imports
from gsp.core.camera import Camera
from gsp.core.viewport import Viewport
from gsp_matplotlib.extra.bufferx import Bufferx
from gsp.types.transbuf import TransBuf
from gsp.visuals.markers import Markers
from gsp.utils.transbuf_utils import TransBufUtils
from .datoviz_renderer import DatovizRenderer
from gsp.utils.unit_utils import UnitUtils
from gsp.utils.math_utils import MathUtils
from gsp_datoviz.utils.converter_utils import ConverterUtils


class DatovizRendererMarkers:
    """Datoviz renderer for Markers visuals."""
    @staticmethod
    def render(
        renderer: DatovizRenderer,
        viewport: Viewport,
        markers: Markers,
        model_matrix: TransBuf,
        camera: Camera,
    ) -> None:
        """Render Markers visuals using Datoviz.

        Args:
            renderer (DatovizRenderer): The Datoviz renderer instance.
            viewport (Viewport): The viewport to render in.
            markers (Markers): The Markers visual to render.
            model_matrix (TransBuf): The model matrix for the visual.
            camera (Camera): The camera used for rendering.
        """
        dvz_panel = renderer._getOrCreateDvzPanel(viewport)

        # =============================================================================
        # Transform vertices with MVP matrix
        # =============================================================================

        vertices_buffer = TransBufUtils.to_buffer(markers.get_positions())
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
        # Convert all attributes to numpy arrays
        # =============================================================================

        sizes_buffer = TransBufUtils.to_buffer(markers.get_sizes())
        face_colors_buffer = TransBufUtils.to_buffer(markers.get_face_colors())
        edge_colors_buffer = TransBufUtils.to_buffer(markers.get_edge_colors())
        edge_widths_buffer = TransBufUtils.to_buffer(markers.get_edge_widths())

        # Convert buffers to numpy arrays)
        sizes_pt2_numpy = Bufferx.to_numpy(sizes_buffer)
        face_colors_numpy = Bufferx.to_numpy(face_colors_buffer)
        edge_colors_numpy = Bufferx.to_numpy(edge_colors_buffer)
        edge_widths_pt_numpy = Bufferx.to_numpy(edge_widths_buffer)

        # Convert sizes from point^2 to pixel
        radius_pt_numpy = np.sqrt(sizes_pt2_numpy / np.pi)
        radius_px_numpy = UnitUtils.point_to_pixel_numpy(radius_pt_numpy, renderer.get_canvas().get_dpi())
        diameter_px_numpy = radius_px_numpy * 2.0 * UnitUtils.device_pixel_ratio()
        diameter_px_numpy = diameter_px_numpy.reshape(-1)

        edge_widths_px_numpy = UnitUtils.point_to_pixel_numpy(edge_widths_pt_numpy, renderer.get_canvas().get_dpi())
        edge_widths_px_numpy = edge_widths_px_numpy * UnitUtils.device_pixel_ratio()
        edge_widths_px_numpy = edge_widths_px_numpy.reshape(-1)

        # =============================================================================
        # Create the datoviz visual if needed
        # =============================================================================

        artist_uuid = f"{viewport.get_uuid()}_{markers.get_uuid()}"

        # Create datoviz_visual if they do not exist
        if artist_uuid not in renderer._dvz_visuals:
            dummy_position_numpy = np.array([[0, 0, 0]], dtype=np.float32).reshape((-1, 3))
            dvz_markers = renderer._dvz_app.marker(position=dummy_position_numpy)
            renderer._dvz_visuals[artist_uuid] = dvz_markers
            # Add the new visual to the panel
            dvz_panel.add(dvz_markers)

        # =============================================================================
        # Update all attributes
        # =============================================================================

        # get the datoviz visual
        dvz_markers = typing.cast(_DvzMarkers, renderer._dvz_visuals[artist_uuid])

        # set attributes
        dvz_markers.set_position(vertices_3d)

        # Set the proper parameters
        dvz_markers.set_size(diameter_px_numpy)
        dvz_markers.set_color(face_colors_numpy)
        dvz_markers.set_linewidth(edge_widths_px_numpy[0])
        dvz_markers.set_edgecolor(edge_colors_numpy[0].tolist())  # datoviz only supports a single edge color

        # sanity check - if edge_widths_px_numpy are not all the same, warn the user
        if not np.all(edge_widths_px_numpy == edge_widths_px_numpy[0]):
            warnings.warn("DatovizRendererMarkers: edge widths per marker are not fully supported by datoviz. " "Using the first edge width for all markers.")
        # sanity check - if edge_colors_numpy are not all the same, warn the user
        if not np.all(edge_colors_numpy == edge_colors_numpy[0]):
            warnings.warn("DatovizRendererMarkers: edge colors per marker are not fully supported by datoviz. " "Using the first edge color for all markers.")

        # Set mode, shape and aspect
        dvz_markers.set_mode("code")
        dvz_markers.set_shape(ConverterUtils.marker_shape_gsp_to_dvz(markers.get_marker_shape()))

        # Determine the `aspect` depending on face and edge colors/widths
        is_face_color_transparent = bool(np.all(face_colors_numpy[:, 3] == 0))
        is_edge_color_transparent = bool(np.all(edge_colors_numpy[:, 3] == 0))
        is_edge_width_zero = bool(np.all(edge_widths_px_numpy == 0))
        has_edge = not is_edge_color_transparent and not is_edge_width_zero
        if not is_face_color_transparent:
            if has_edge:
                dvz_markers.set_aspect("outline")
            else:
                dvz_markers.set_aspect("filled")
        else:
            dvz_markers.set_aspect("stroke")
