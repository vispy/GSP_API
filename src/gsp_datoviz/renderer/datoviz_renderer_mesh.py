"""Datoviz renderer for Mesh visuals."""

# stdlib imports
import typing
import warnings

# pip imports
import numpy as np
from datoviz.visuals import Mesh as _DvzMesh

# local imports
from gsp.core.camera import Camera
from gsp.core.viewport import Viewport
from gsp_matplotlib.extra.bufferx import Bufferx
from gsp.types.transbuf import TransBuf
from gsp.visuals.mesh import Mesh
from gsp.utils.transbuf_utils import TransBufUtils
from .datoviz_renderer import DatovizRenderer
from gsp.utils.unit_utils import UnitUtils
from gsp.utils.math_utils import MathUtils
from gsp_datoviz.utils.converter_utils import ConverterUtils


class DatovizRendererMesh:
    """Datoviz renderer for Mesh visuals."""

    @staticmethod
    def render(
        renderer: DatovizRenderer,
        viewport: Viewport,
        mesh: Mesh,
        model_matrix: TransBuf,
        camera: Camera,
    ) -> None:
        """Render Mesh visuals using Datoviz.

        Args:
            renderer (DatovizRenderer): The Datoviz renderer instance.
            viewport (Viewport): The viewport to render in.
            mesh (Mesh): The Mesh visual to render.
            model_matrix (TransBuf): The model matrix for the visual.
            camera (Camera): The camera used for rendering.
        """
        dvz_panel = renderer._getOrCreateDvzPanel(viewport)

        # =============================================================================
        # Transform vertices with MVP matrix
        # =============================================================================

        mesh_geometry = mesh.get_geometry()
        mesh_material = mesh.get_material()

        vertices_transbuf = mesh_geometry.get_positions()

        vertices_buffer = TransBufUtils.to_buffer(vertices_transbuf)
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

        indices_buffer = TransBufUtils.to_buffer(mesh_geometry.get_indices())
        uvs_buffer = TransBufUtils.to_buffer(mesh_geometry.get_uvs())
        normals_buffer = TransBufUtils.to_buffer(mesh_geometry.get_normals())
        colors_buffer = TransBufUtils.to_buffer(mesh_material.get_colors())

        # Convert buffers to numpy arrays
        indices_numpy = Bufferx.to_numpy(indices_buffer).flatten()
        uvs_numpy = Bufferx.to_numpy(uvs_buffer)
        normals_numpy = Bufferx.to_numpy(normals_buffer)
        colors_numpy = Bufferx.to_numpy(colors_buffer)

        # =============================================================================
        # Sanity checks attributes buffers
        # =============================================================================

        Mesh.sanity_check_attributes_buffer(
            mesh.get_geometry(),
            mesh.get_material(),
        )

        # =============================================================================
        # Create the datoviz visual if needed
        # =============================================================================

        artist_uuid = f"{viewport.get_uuid()}_{mesh.get_uuid()}"

        # Create datoviz_visual if they do not exist
        if artist_uuid not in renderer._dvz_visuals:
            dummy_position_numpy = np.array([[0, 0, 0]], dtype=np.float32).reshape((-1, 3))
            # dvz_mesh = renderer._dvz_app.mesh(
            #     position=dummy_position_numpy
            # )
            dvz_mesh = renderer._dvz_app.mesh(
                position=vertices_3d,
                normal=normals_numpy,
                color=colors_numpy,
                # texcoords=texcoords,
                index=indices_numpy,
                # lighting=True,
                contour=True,
            )
            renderer._dvz_visuals[artist_uuid] = dvz_mesh
            # Add the new visual to the panel
            dvz_panel.add(dvz_mesh)

        # =============================================================================
        # Update all attributes
        # =============================================================================

        # # get the datoviz visual
        # dvz_mesh = typing.cast(_DvzMesh, renderer._dvz_visuals[artist_uuid])

        # # set attributes
        # dvz_mesh.set_position(vertices_3d)
        # dvz_mesh.set_normal(normals_numpy)
        # dvz_mesh.set_index(indices_numpy)
        # # dvz_mesh.set_texcoord(uvs_numpy)
        # dvz_mesh.set_color(colors_numpy)
