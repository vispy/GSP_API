"""Matplotlib renderer for Mesh objects."""

# pip imports
import typing
import matplotlib.collections
import matplotlib.artist

# local imports
from gsp.core.camera import Camera
from gsp.core.viewport import Viewport
from gsp.utils.math_utils import MathUtils
from gsp.visuals.mesh import Mesh
from gsp.utils.transbuf_utils import TransBufUtils
from gsp.types.transbuf import TransBuf
from .matplotlib_renderer import MatplotlibRenderer
from ..extra.bufferx import Bufferx
from ..utils.converter_utils import ConverterUtils


class RendererMesh:
    """Renderer for Mesh objects using Matplotlib."""

    @staticmethod
    def render(
        renderer: MatplotlibRenderer,
        viewport: Viewport,
        mesh: Mesh,
        model_matrix: TransBuf,
        camera: Camera,
    ) -> list[matplotlib.artist.Artist]:
        """Render the given Mesh object onto the specified viewport using Matplotlib.

        Args:
            renderer (MatplotlibRenderer): The renderer instance.
            viewport (Viewport): The viewport to render onto.
            mesh (Mesh): The Mesh object containing mesh data.
            model_matrix (TransBuf): The model transformation matrix.
            camera (Camera): The camera providing view and projection matrices.

        Returns:
            list[matplotlib.artist.Artist]: A list of Matplotlib artist objects created or updated
        """
        # =============================================================================
        # Transform vertices with MVP matrix
        # =============================================================================

        vertices_buffer = TransBufUtils.to_buffer(mesh.get_positions())
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
        sizes_buffer = TransBufUtils.to_buffer(mesh.get_sizes())
        face_colors_buffer = TransBufUtils.to_buffer(mesh.get_face_colors())
        edge_colors_buffer = TransBufUtils.to_buffer(mesh.get_edge_colors())
        edge_widths_buffer = TransBufUtils.to_buffer(mesh.get_edge_widths())

        # Convert buffers to numpy arrays
        sizes_numpy = Bufferx.to_numpy(sizes_buffer).reshape(-1)
        face_colors_numpy = Bufferx.to_numpy(face_colors_buffer) / 255.0  # normalize to [0, 1] range
        edge_colors_numpy = Bufferx.to_numpy(edge_colors_buffer) / 255.0  # normalize to [0, 1] range
        edge_widths_numpy = Bufferx.to_numpy(edge_widths_buffer).flatten()

        # =============================================================================
        # Sanity checks attributes buffers
        # =============================================================================

        Mesh.sanity_check_attributes_buffer(
            mesh.get_marker_shape(),
            vertices_buffer,
            sizes_buffer,
            face_colors_buffer,
            edge_colors_buffer,
            edge_widths_buffer,
        )

        # =============================================================================
        # Create the artists if needed
        # =============================================================================

        artist_uuid = f"{viewport.get_uuid()}_{mesh.get_uuid()}"

        if artist_uuid not in renderer._artists:
            axes = renderer.get_mpl_axes_for_viewport(viewport)
            mpl_marker_shape = ConverterUtils.marker_shape_gsp_to_mpl(mesh.get_marker_shape())
            mpl_path_collection = axes.scatter([], [], marker=mpl_marker_shape)
            mpl_path_collection.set_visible(False)
            # hide until properly positioned and sized
            renderer._artists[artist_uuid] = mpl_path_collection
            axes.add_artist(mpl_path_collection)

        # =============================================================================
        # Get existing artists
        # =============================================================================

        mpl_path_collection = typing.cast(matplotlib.collections.PathCollection, renderer._artists[artist_uuid])
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
