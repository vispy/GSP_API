# pip imports
import typing
import matplotlib.axes
import matplotlib.collections
import matplotlib.artist
import numpy as np

# local imports
from gsp.core.camera import Camera
from gsp.utils.math_utils import MathUtils
from gsp.visuals.paths import Paths
from gsp.utils.transbuf_utils import TransBufUtils
from gsp.types.transbuf import TransBuf
from gsp.types.buffer_type import BufferType
from .matplotlib_renderer import MatplotlibRenderer
from ..extra.bufferx import Bufferx


class RendererPaths:
    @staticmethod
    def render(
        renderer: MatplotlibRenderer,
        axes: matplotlib.axes.Axes,
        visual: Paths,
        model_matrix: TransBuf,
        camera: Camera,
    ) -> list[matplotlib.artist.Artist]:
        paths: Paths = visual

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

        # Convert 3D vertices to 2D - shape (N, 2)
        vertices_2d = vertices_3d_transformed[:, :2]

        # =============================================================================
        # Convert all attributes to numpy arrays
        # =============================================================================

        # Convert all attributes to buffer
        path_sizes_buffer = TransBufUtils.to_buffer(paths.get_path_sizes())
        colors_buffer = TransBufUtils.to_buffer(paths.get_colors())
        line_widths_buffer = TransBufUtils.to_buffer(paths.get_line_widths())

        # Convert buffers to numpy arrays
        path_sizes_numpy = Bufferx.to_numpy(path_sizes_buffer)
        colors_numpy = Bufferx.to_numpy(colors_buffer) / 255.0  # normalize to [0, 1] range
        line_widths_numpy = Bufferx.to_numpy(line_widths_buffer)
        line_widths_numpy = line_widths_numpy.reshape(-1)

        # =============================================================================
        #
        # =============================================================================
        # mpl_paths is of shape (M, 2, 2) where M is total number of line segments across all paths
        mpl_paths = np.zeros((0, 2, 2), dtype=np.float32)
        # mpl_colors is of shape (M, 4)
        mpl_colors = np.zeros((0, 4), dtype=np.float32)
        # mpl_line_widths is of shape (M,)
        mpl_line_widths = np.zeros((0,), dtype=np.float32)

        for path_index, path_size in enumerate(path_sizes_numpy):
            path_start = int(np.sum(path_sizes_numpy[:path_index]))
            path_size_int = int(path_size)
            path_vertices_2d = vertices_2d[path_start : path_start + path_size_int]

            # Create segments for this path
            path_mpl_paths = np.concatenate([path_vertices_2d[:-1].reshape(-1, 1, 2), path_vertices_2d[1:].reshape(-1, 1, 2)], axis=1)
            mpl_paths = np.vstack([mpl_paths, path_mpl_paths])

            mpl_colors = np.vstack([mpl_colors, colors_numpy[path_start : path_start + path_size_int - 1]])
            mpl_line_widths = np.hstack([mpl_line_widths, line_widths_numpy[path_start : path_start + path_size_int - 1]])

        # =============================================================================
        # Create the artists if needed
        # =============================================================================

        if paths.get_uuid() not in renderer._artists:
            mpl_line_collection = matplotlib.collections.LineCollection([])
            mpl_line_collection.set_visible(False)
            # hide until properly positioned and sized
            renderer._artists[paths.get_uuid()] = mpl_line_collection
            axes.add_artist(mpl_line_collection)

        # =============================================================================
        # Get existing artists
        # =============================================================================

        mpl_line_collection = typing.cast(matplotlib.collections.LineCollection, renderer._artists[paths.get_uuid()])
        mpl_line_collection.set_visible(True)

        # =============================================================================
        # Update artists
        # =============================================================================

        mpl_line_collection.set_paths(typing.cast(list, mpl_paths))
        mpl_line_collection.set_color(typing.cast(list, mpl_colors))
        mpl_line_collection.set_linewidth(typing.cast(list, mpl_line_widths))
        mpl_line_collection.set_capstyle("round")
        mpl_line_collection.set_joinstyle("round")

        # Return the list of artists created/updated
        changed_artists: list[matplotlib.artist.Artist] = []
        changed_artists.append(mpl_line_collection)
        return changed_artists
