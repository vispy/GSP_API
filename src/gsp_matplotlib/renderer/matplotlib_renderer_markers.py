# pip imports
import typing
import matplotlib.axes
import matplotlib.collections
import matplotlib.artist
import numpy as np

# local imports
from gsp.core.camera import Camera
from gsp.utils.group_utils import GroupUtils
from gsp.utils.math_utils import MathUtils
from gsp.visuals import Markers
from gsp.utils.transbuf_utils import TransBufUtils
from gsp.types.transbuf import TransBuf
from gsp.types.buffer_type import BufferType
from .matplotlib_renderer import MatplotlibRenderer
from ..extra.bufferx import Bufferx
from ..utils.converter_utils import ConverterUtils


class RendererMarkers:
    @staticmethod
    def render(
        renderer: MatplotlibRenderer,
        axes: matplotlib.axes.Axes,
        markers: Markers,
        model_matrix: TransBuf,
        camera: Camera,
    ) -> list[matplotlib.artist.Artist]:
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

        # Convert 3D vertices to 2D - shape (N, 2)
        vertices_2d = vertices_3d_transformed[:, :2]

        # =============================================================================
        # Convert all attributes to numpy arrays
        # =============================================================================

        # Convert all attributes to buffer
        sizes_buffer = TransBufUtils.to_buffer(markers.get_sizes())
        face_colors_buffer = TransBufUtils.to_buffer(markers.get_face_colors())
        edge_colors_buffer = TransBufUtils.to_buffer(markers.get_edge_colors())
        edge_widths_buffer = TransBufUtils.to_buffer(markers.get_edge_widths())

        # Convert buffers to numpy arrays
        sizes_numpy = Bufferx.to_numpy(sizes_buffer).reshape(-1)
        face_colors_numpy = Bufferx.to_numpy(face_colors_buffer) / 255.0  # normalize to [0, 1] range
        edge_colors_numpy = Bufferx.to_numpy(edge_colors_buffer) / 255.0  # normalize to [0, 1] range
        edge_widths_numpy = Bufferx.to_numpy(edge_widths_buffer).flatten()

        # =============================================================================
        # Create the artists if needed
        # =============================================================================

        if markers.get_uuid() not in renderer._artists:
            mpl_marker_shape = ConverterUtils.marker_shape_gsp_to_mpl(markers.get_marker_shape())
            mpl_path_collection = axes.scatter([], [], marker=mpl_marker_shape)
            mpl_path_collection.set_visible(False)
            # hide until properly positioned and sized
            renderer._artists[markers.get_uuid()] = mpl_path_collection
            axes.add_artist(mpl_path_collection)

        # =============================================================================
        # Get existing artists
        # =============================================================================

        mpl_path_collection = typing.cast(matplotlib.collections.PathCollection, renderer._artists[markers.get_uuid()])
        mpl_path_collection.set_visible(True)

        # =============================================================================
        # Update artists
        # =============================================================================

        mpl_path_collection.set_offsets(offsets=vertices_2d)
        mpl_path_collection.set_sizes(typing.cast(list, sizes_numpy))
        mpl_path_collection.set_facecolor(typing.cast(list, face_colors_numpy))
        mpl_path_collection.set_edgecolor(typing.cast(list, edge_colors_numpy))
        mpl_path_collection.set_linewidth(typing.cast(list, edge_widths_numpy))

        # Return the list of artists created/updated
        return [mpl_path_collection]
