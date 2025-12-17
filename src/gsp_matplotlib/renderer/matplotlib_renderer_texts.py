"""Renderer for Texts using Matplotlib."""

# pip imports
import typing
import matplotlib.text
import matplotlib.artist
import numpy as np

# local imports
from gsp.core.camera import Camera
from gsp.core.viewport import Viewport
from gsp.utils.math_utils import MathUtils
from gsp.visuals.texts import Texts
from gsp.utils.transbuf_utils import TransBufUtils
from gsp.types.transbuf import TransBuf
from .matplotlib_renderer import MatplotlibRenderer
from ..extra.bufferx import Bufferx


class RendererTexts:
    """Renderer for Texts using Matplotlib."""

    @staticmethod
    def render(
        renderer: MatplotlibRenderer,
        viewport: Viewport,
        texts: Texts,
        model_matrix: TransBuf,
        camera: Camera,
    ) -> list[matplotlib.artist.Artist]:
        """Render Texts visual using Matplotlib.

        Args:
            renderer: The MatplotlibRenderer instance.
            viewport: The Viewport in which to render.
            texts: The Texts visual to render.
            model_matrix: The model transformation matrix as a TransBuf.
            camera: The Camera providing view and projection matrices.
        
        Returns:
            list[matplotlib.artist.Artist]: List of Matplotlib artists created/updated.
        """
        # =============================================================================
        # Transform vertices with MVP matrix
        # =============================================================================

        vertices_buffer = TransBufUtils.to_buffer(texts.get_positions())
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
        colors_buffer = TransBufUtils.to_buffer(texts.get_colors())
        font_sizes_buffer = TransBufUtils.to_buffer(texts.get_font_sizes())
        anchors_buffer = TransBufUtils.to_buffer(texts.get_anchors())
        angles_buffer = TransBufUtils.to_buffer(texts.get_angles())

        # Convert buffers to numpy arrays
        font_sizes_numpy = Bufferx.to_numpy(font_sizes_buffer).flatten()
        colors_numpy = Bufferx.to_numpy(colors_buffer) / 255.0  # normalize to [0, 1] range
        anchors_numpy = Bufferx.to_numpy(anchors_buffer)
        angles_numpy = Bufferx.to_numpy(angles_buffer).flatten()

        # =============================================================================
        # Create the artists if needed
        # =============================================================================

        artist_uuid_sample = f"{viewport.get_uuid()}_{texts.get_uuid()}_0"
        if artist_uuid_sample not in renderer._artists:
            mpl_axes = renderer.get_mpl_axes_for_viewport(viewport)
            for text_index in range(len(texts.get_strings())):
                artist_uuid = f"{viewport.get_uuid()}_{texts.get_uuid()}_{text_index}"
                mpl_text = matplotlib.text.Text()
                mpl_text.set_visible(False)
                # hide until properly positioned and sized
                renderer._artists[artist_uuid] = mpl_text
                mpl_axes.add_artist(mpl_text)

        # =============================================================================
        # Get existing artists
        # =============================================================================

        changed_artists: list[matplotlib.artist.Artist] = []
        for text_index in range(len(texts.get_strings())):
            artist_uuid = f"{viewport.get_uuid()}_{texts.get_uuid()}_{text_index}"
            mpl_text = typing.cast(matplotlib.text.Text, renderer._artists[artist_uuid])
            mpl_text.set_visible(True)

            # =============================================================================
            # Update artists
            # =============================================================================

            mpl_text.set_x(vertices_2d[text_index, 0])
            mpl_text.set_y(vertices_2d[text_index, 1])
            mpl_text.set_text(texts.get_strings()[text_index])
            mpl_text.set_rotation(angles_numpy[text_index] / np.pi * 180.0)  # convert rad to deg
            print(f"angles_numpy[{text_index}]: {angles_numpy[text_index]}")

            ha_label = "center" if anchors_numpy[text_index, 0] == 0.0 else "right" if anchors_numpy[text_index, 0] == 1.0 else "left"
            mpl_text.set_horizontalalignment(ha_label)
            va_label = "center" if anchors_numpy[text_index, 1] == 0.0 else "top" if anchors_numpy[text_index, 1] == 1.0 else "bottom"
            mpl_text.set_verticalalignment(va_label)

            mpl_text.set_fontfamily(texts.get_font_name())
            mpl_text.set_fontsize(font_sizes_numpy[text_index])
            mpl_text.set_color(typing.cast(tuple, colors_numpy[text_index]))

            # Return the list of artists created/updated
            changed_artists.append(mpl_text)

        return changed_artists
