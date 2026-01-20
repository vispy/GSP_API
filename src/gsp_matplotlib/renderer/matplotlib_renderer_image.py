"""Renderer for Image using Matplotlib."""

# pip imports
import typing
import matplotlib.image
import matplotlib.artist

# local imports
from gsp.core.camera import Camera
from gsp.core.viewport import Viewport
from gsp.utils.math_utils import MathUtils
from gsp.visuals.image import Image
from gsp.utils.transbuf_utils import TransBufUtils
from gsp.types.transbuf import TransBuf
from gsp.types.image_interpolation import ImageInterpolation
from .matplotlib_renderer import MatplotlibRenderer
from ..extra.bufferx import Bufferx


class RendererImage:
    """Renderer for Image using Matplotlib."""

    @staticmethod
    def render(
        renderer: MatplotlibRenderer,
        viewport: Viewport,
        image: Image,
        model_matrix: TransBuf,
        camera: Camera,
    ) -> list[matplotlib.artist.Artist]:
        """Render Image visual using Matplotlib.

        Args:
            renderer: The MatplotlibRenderer instance.
            viewport: The Viewport in which to render.
            image: The Image visual to render.
            model_matrix: The model transformation matrix as a TransBuf.
            camera: The Camera providing view and projection matrices.

        Returns:
            list[matplotlib.artist.Artist]: List of Matplotlib artists created/updated.
        """
        # =============================================================================
        # Transform vertices with MVP matrix
        # =============================================================================

        vertices_buffer = TransBufUtils.to_buffer(image.get_position())
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

        gsp_texture = image.get_texture()

        # Convert all attributes to buffer
        texture_buffer = TransBufUtils.to_buffer(gsp_texture.get_data())

        # Convert buffers to numpy arrays
        texture_width = gsp_texture.get_width()
        texture_height = gsp_texture.get_height()
        texture_numpy = Bufferx.to_numpy(texture_buffer).reshape((texture_height, texture_width, -1))

        # =============================================================================
        # Sanity checks attributes buffers
        # =============================================================================

        Image.sanity_check_attributes_buffer(
            image.get_texture(),
            vertices_buffer,
            image.get_image_extent(),
            image.get_interpolation(),
        )

        # =============================================================================
        # Create the artists if needed
        # =============================================================================

        artist_uuid = f"{viewport.get_uuid()}_{image.get_uuid()}"
        if artist_uuid not in renderer._artists:
            axes = renderer.get_mpl_axes_for_viewport(viewport)
            mpl_axes_image = matplotlib.image.AxesImage(axes)
            mpl_axes_image.set_visible(False)
            # hide until properly positioned and sized
            renderer._artists[artist_uuid] = mpl_axes_image
            axes.add_artist(mpl_axes_image)

        # =============================================================================
        # Get existing artists
        # =============================================================================

        mpl_axes_image = typing.cast(matplotlib.image.AxesImage, renderer._artists[artist_uuid])
        mpl_axes_image.set_visible(True)

        # =============================================================================
        # Update artists
        # =============================================================================

        gsp_texture = image.get_texture()

        # create random image
        mpl_axes_image.set_data(texture_numpy)

        # set extent
        image_extent = image.get_image_extent()
        mpl_extent = (
            vertices_2d[0, 0] + image_extent[0],  # TODO get w from transformed vertices and divide extent by w
            vertices_2d[0, 0] + image_extent[1],
            vertices_2d[0, 1] + image_extent[2],
            vertices_2d[0, 1] + image_extent[3],
        )
        mpl_axes_image.set_extent(mpl_extent)

        # set interpolation
        if image.get_interpolation() == ImageInterpolation.NEAREST:
            mpl_axes_image.set_interpolation("nearest")
        elif image.get_interpolation() == ImageInterpolation.LINEAR:
            mpl_axes_image.set_interpolation("bilinear")
        else:
            mpl_axes_image.set_interpolation("nearest")

        # Return the list of artists created/updated
        changed_artists: list[matplotlib.artist.Artist] = []
        changed_artists.append(mpl_axes_image)
        return changed_artists
