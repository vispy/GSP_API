# pip imports
import typing
import matplotlib.axes
import matplotlib.collections
import matplotlib.artist
import numpy as np

# local imports
from gsp.core.camera import Camera
from gsp.utils.math_utils import MathUtils
from gsp.core.viewport import Viewport
from gsp.utils.transbuf_utils import TransBufUtils
from gsp.types.transbuf import TransBuf
from gsp.types.buffer_type import BufferType
from gsp.visuals.segments import Segments
from .matplotlib_renderer import MatplotlibRenderer
from ..extra.bufferx import Bufferx
from ..utils.converter_utils import ConverterUtils


class RendererSegments:
    @staticmethod
    def render(
        renderer: MatplotlibRenderer,
        viewport: Viewport,
        segments: Segments,
        model_matrix: TransBuf,
        camera: Camera,
    ) -> list[matplotlib.artist.Artist]:
        # =============================================================================
        # Transform vertices with MVP matrix
        # =============================================================================

        vertices_buffer = TransBufUtils.to_buffer(segments.get_positions())
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
        colors_buffer = TransBufUtils.to_buffer(segments.get_colors())
        line_widths_buffer = TransBufUtils.to_buffer(segments.get_line_widths())

        # Convert buffers to numpy arrays
        positions_numpy = vertices_2d.reshape(-1, 2, 2)
        colors_numpy = Bufferx.to_numpy(colors_buffer) / 255.0  # normalize to [0, 1] range
        line_widths_numpy = Bufferx.to_numpy(line_widths_buffer)
        line_widths_numpy = line_widths_numpy.reshape(-1)

        # =============================================================================
        # Create the artists if needed
        # =============================================================================

        if segments.get_uuid() not in renderer._artists:
            mpl_line_collection = matplotlib.collections.LineCollection([])
            mpl_line_collection.set_visible(False)
            # hide until properly positioned and sized
            renderer._artists[segments.get_uuid()] = mpl_line_collection
            axes = renderer.get_axes_for_viewport(viewport)
            axes.add_artist(mpl_line_collection)

        # =============================================================================
        # Get existing artists
        # =============================================================================

        mpl_line_collection = typing.cast(matplotlib.collections.LineCollection, renderer._artists[segments.get_uuid()])
        mpl_line_collection.set_visible(True)

        # =============================================================================
        # Update artists
        # =============================================================================

        mpl_line_collection.set_paths(typing.cast(list, positions_numpy))
        mpl_line_collection.set_color(typing.cast(list, colors_numpy))
        mpl_line_collection.set_linewidth(typing.cast(list, line_widths_numpy))
        mpl_line_collection.set_capstyle(ConverterUtils.cap_style_gsp_to_mpl(segments.get_cap_style()))

        # Return the list of artists created/updated
        changed_artists: list[matplotlib.artist.Artist] = []
        changed_artists.append(mpl_line_collection)
        return changed_artists
