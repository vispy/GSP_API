"""Datoviz renderer for Points visuals."""

# stdlib imports
from typing import Sequence
import typing

# pip imports
import numpy as np
from datoviz.visuals import Image as _DvzImage
from datoviz._texture import Texture as _DvzTexture

# local imports
from .datoviz_renderer import DatovizRenderer
from gsp.core.camera import Camera
from gsp.core.canvas import Canvas
from gsp.core.viewport import Viewport
from gsp_matplotlib.extra.bufferx import Bufferx
from gsp.types.transbuf import TransBuf
from gsp.types.image_interpolation import ImageInterpolation
from gsp.visuals.points import Points
from gsp.visuals.image import Image
from gsp.utils.transbuf_utils import TransBufUtils
from gsp.utils.group_utils import GroupUtils
from gsp.utils.math_utils import MathUtils
from gsp.utils.unit_utils import UnitUtils


class DatovizRendererImage:
    """Datoviz renderer for Image visuals."""

    @staticmethod
    def render(
        renderer: DatovizRenderer,
        viewport: Viewport,
        image: Image,
        model_matrix: TransBuf,
        camera: Camera,
    ) -> None:
        """Render Image visuals using Datoviz.

        Args:
            renderer (DatovizRenderer): The Datoviz renderer instance.
            viewport (Viewport): The viewport to render in.
            image (Image): The Image visual to render.
            model_matrix (TransBuf): The model matrix for the visual.
            camera (Camera): The camera used for rendering.
        """
        dvz_panel = renderer._getOrCreateDvzPanel(viewport)

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

        # Convert 3D vertices to 3d - shape (N, 3)
        vertices_3d = np.ascontiguousarray(vertices_3d_transformed, dtype=np.float32)

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
        # Create the datoviz visual if needed
        # =============================================================================

        # get or create datoviz texture
        texture_uuid = f"{gsp_texture.get_uuid()}"
        if texture_uuid not in renderer._dvz_textures:
            # set interpolation
            if image.get_interpolation() == ImageInterpolation.NEAREST:
                dvz_image_interpolation = "nearest"
            elif image.get_interpolation() == ImageInterpolation.LINEAR:
                dvz_image_interpolation = "linear"
            else:
                dvz_image_interpolation = "nearest"
            dvz_texture = renderer._dvz_app.texture_2D(image=texture_numpy, interpolation=dvz_image_interpolation)
            renderer._dvz_textures[texture_uuid] = dvz_texture
        dvz_texture = typing.cast(_DvzTexture, renderer._dvz_textures[texture_uuid])

        artist_uuid = f"{viewport.get_uuid()}_{image.get_uuid()}"
        # Create datoviz_visual if they do not exist
        if artist_uuid not in renderer._dvz_visuals:
            dvz_image = renderer._dvz_app.image(
                position=vertices_3d,
                unit="ndc",
            )
            dvz_image.set_texture(dvz_texture)
            renderer._dvz_visuals[artist_uuid] = dvz_image
            # Add the new visual to the panel
            dvz_panel.add(dvz_image)

        # =============================================================================
        # Update all attributes
        # =============================================================================

        # get the datoviz visual
        dvz_image = typing.cast(_DvzImage, renderer._dvz_visuals[artist_uuid])

        # set attributes
        dvz_image.set_position(vertices_3d)

        # dvz_size = np.array([[gsp_texture.get_width() / viewport.get_width(), gsp_texture.get_height() / viewport.get_height()]], dtype=np.float32)
        # dvz_image.set_size(dvz_size)

        image_extent = image.get_image_extent()
        dvz_size = np.array([[image_extent[1] - image_extent[0], image_extent[3] - image_extent[2]]], dtype=np.float32)
        dvz_image.set_size(dvz_size)

        dvz_texcoords = np.array([[0, 0, 1, 1]], dtype=np.float32)
        dvz_image.set_texcoords(dvz_texcoords)
