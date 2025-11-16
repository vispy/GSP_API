# pip imports
import typing
import matplotlib.axes
import matplotlib.collections
import matplotlib.artist

# local imports
from gsp.core.camera import Camera
from gsp.core.viewport import Viewport
from gsp.types.visual_base import VisualBase
from gsp.utils.group_utils import GroupUtils
from gsp.visuals.pixels import Pixels
from gsp.utils.transbuf_utils import TransBufUtils
from gsp.utils.math_utils import MathUtils
from gsp.types.transbuf import TransBuf
from gsp_matplotlib.renderer import MatplotlibRenderer
from gsp.utils.unit_utils import UnitUtils
from ..extra.bufferx import Bufferx


class RendererPixels:
    @staticmethod
    def render(
        renderer: MatplotlibRenderer,
        viewport: Viewport,
        pixels: Pixels,
        model_matrix: TransBuf,
        camera: Camera,
    ) -> list[matplotlib.artist.Artist]:
        # =============================================================================
        # Transform vertices with MVP matrix
        # =============================================================================

        vertices_buffer = TransBufUtils.to_buffer(pixels.get_positions())
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
        color_buffer = TransBufUtils.to_buffer(pixels.get_colors())

        # Convert buffers to numpy arrays
        colors_numpy = Bufferx.to_numpy(color_buffer) / 255.0  # normalize to [0, 1] range

        # Sanity check - check visual attributes
        Pixels.sanity_check_attribute_buffers(vertices_buffer, color_buffer, pixels.get_groups())

        # =============================================================================
        #   Compute indices_per_group for groups depending on the type of groups
        # =============================================================================

        indices_per_group = GroupUtils.compute_indices_per_group(vertices_numpy.__len__(), pixels.get_groups())
        group_count = GroupUtils.get_group_count(vertices_numpy.__len__(), pixels.get_groups())

        # =============================================================================
        # Create the artists if needed
        # =============================================================================

        artist_uuid_prefix = f"{viewport.get_uuid()}_{pixels.get_uuid()}"

        # update stored group count
        old_group_count = None
        if artist_uuid_prefix in renderer._group_count:
            old_group_count = renderer._group_count[artist_uuid_prefix]
        renderer._group_count[artist_uuid_prefix] = group_count

        # If the group count has changed, destroy old artists
        if old_group_count is not None and old_group_count != group_count:
            RendererPixels.destroy_artists(renderer, viewport, pixels, old_group_count)

        # Create artists if they do not exist
        artist_uuid_sample = f"{artist_uuid_prefix}_group_0"
        if artist_uuid_sample not in renderer._artists:
            RendererPixels.create_artists(renderer, viewport, pixels, group_count)

        # =============================================================================
        # Update matplotlib for each group
        # =============================================================================

        changed_artists: list[matplotlib.artist.Artist] = []
        for group_index in range(group_count):
            group_uuid = f"{artist_uuid_prefix}_group_{group_index}"

            # =============================================================================
            # Get existing artists
            # =============================================================================

            mpl_path_collection = typing.cast(matplotlib.collections.PathCollection, renderer._artists[group_uuid])
            mpl_path_collection.set_visible(True)
            changed_artists.append(mpl_path_collection)

            # =============================================================================
            # Update artists
            # =============================================================================

            mpl_path_collection.set_offsets(offsets=vertices_2d[indices_per_group[group_index]])
            mpl_path_collection.set_facecolor(typing.cast(list, colors_numpy[group_index]))

        # Return the list of artists created/updated
        return changed_artists

    # =============================================================================
    #
    # =============================================================================

    @staticmethod
    def create_artists(renderer: MatplotlibRenderer, viewport: Viewport, visual: VisualBase, group_count: int) -> None:
        """Create the artists associated with the given visual and group count."""

        axes = renderer.get_axes_for_viewport(viewport)
        artist_uuid_prefix = f"{viewport.get_uuid()}_{visual.get_uuid()}"
        # compute 1 pixel size in points squared for matplotlib sizing
        assert axes.figure.get_dpi() is not None, "Canvas DPI must be set for proper pixel sizing"
        size_pt = UnitUtils.pixel_to_point(1.0, axes.figure.get_dpi())
        size_squared_pt = size_pt * size_pt

        for group_index in range(group_count):
            mpl_path_collection = axes.scatter([], [], s=size_squared_pt, marker="o")
            mpl_path_collection.set_antialiased(True)
            mpl_path_collection.set_linewidth(0)
            mpl_path_collection.set_visible(False)
            # hide until properly positioned and sized
            group_uuid = f"{artist_uuid_prefix}_group_{group_index}"
            renderer._artists[group_uuid] = mpl_path_collection
            axes.add_artist(mpl_path_collection)

    @staticmethod
    def destroy_artists(renderer: MatplotlibRenderer, viewport: Viewport, visual: VisualBase, group_count: int) -> None:
        """Destroy the artists associated with the given visual and group count.

        Trigger a bug in matplotlib where artists are not properly removed from the axes.
        """
        axes = renderer.get_axes_for_viewport(viewport)
        artist_uuid_prefix = f"{viewport.get_uuid()}_{visual.get_uuid()}"
        for group_index in range(group_count):
            group_uuid = f"{artist_uuid_prefix}_group_{group_index}"
            mpl_path_collection = typing.cast(matplotlib.collections.PathCollection, renderer._artists[group_uuid])
            del renderer._artists[group_uuid]
            mpl_path_collection.remove()

            # axes.collections.remove(mpl_path_collection)
            # axes.collections.remove(axes.collections.index(mpl_path_collection))

            ax = axes
            artist = mpl_path_collection

            print("Artist:", artist)
            print("In ax.artists?", artist in ax.artists)
            print("In ax.patches?", artist in ax.patches)
            print("In ax.lines?", artist in ax.lines)
            print("In ax.collections?", artist in ax.collections)
            print("In ax.texts?", artist in ax.texts)
            print("Figure art?", artist in getattr(ax.figure, "artists", []))
