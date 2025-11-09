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
from gsp.visuals import pixels
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

        # =============================================================================
        #   Compute indices_per_group for groups depending on the type of groups
        # =============================================================================

        indices_per_group = GroupUtils.compute_indices_per_group(vertices_numpy.__len__(), paths.get_groups())
        group_count = GroupUtils.get_group_count(vertices_numpy.__len__(), paths.get_groups())

        assert group_count == 1, f"MatplotlibRenderer for Paths currently only supports a single group, but got {group_count} groups."

        # =============================================================================
        # Create the artists if needed
        # =============================================================================

        artist_uuid_sample = f"{visual.get_uuid()}_group_0"
        if artist_uuid_sample not in renderer._artists:
            for group_index in range(group_count):
                mpl_line_collection = matplotlib.collections.LineCollection([])
                mpl_line_collection.set_visible(False)
                # hide until properly positioned and sized
                group_uuid = f"{visual.get_uuid()}_group_{group_index}"
                renderer._artists[group_uuid] = mpl_line_collection
                axes.add_artist(mpl_line_collection)

        # =============================================================================
        # Update matplotlib for each group
        # =============================================================================

        changed_artists: list[matplotlib.artist.Artist] = []
        for group_index in range(group_count):
            group_uuid = f"{visual.get_uuid()}_group_{group_index}"

            # =============================================================================
            # Get existing artists
            # =============================================================================

            mpl_line_collection = typing.cast(matplotlib.collections.LineCollection, renderer._artists[group_uuid])
            mpl_line_collection.set_visible(True)
            changed_artists.append(mpl_line_collection)

            # =============================================================================
            # Update artists
            # =============================================================================

            mpl_line_collection.set_paths(segments=vertices_2d[indices_per_group[group_index]])
            mpl_line_collection.set_color(typing.cast(list, colors_numpy[group_index]))
            mpl_line_collection.set_linewidth(typing.cast(list, line_widths_numpy[group_index]))

        # Return the list of artists created/updated
        return changed_artists
