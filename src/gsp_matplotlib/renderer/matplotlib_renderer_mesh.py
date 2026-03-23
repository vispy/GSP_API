# stdlib imports
import typing

# pip imports
import matplotlib.artist
import numpy as np


# local imports
from gsp.constants import Constants
from gsp.visuals.mesh import Mesh
from gsp.materials import MeshBasicMaterial, MeshPhongMaterial, MeshNormalMaterial, MeshDepthMaterial, MeshTexturedMaterial
from .matplotlib_renderer import MatplotlibRenderer
from gsp.core.camera import Camera
from gsp.core.viewport import Viewport
from gsp.types.transbuf import TransBuf
from gsp.utils.math_utils import MathUtils
from ..extra.bufferx import Bufferx
from gsp.utils.transbuf_utils import TransBufUtils

# from ..cameras.camera import Camera
# from ..math.transform_utils import TransformUtils
# from gsp.geometry.geometry_utils import GeometryUtils

# https://chatgpt.com/c/68ee0eab-776c-8331-b44a-f131ba3f166b
# local -> world -> view -> clip (NDC) -> screen (2D)

# local -> world : coord in world space
# world -> view : coord in camera space
# view -> clip (NDC) : coord in normalized device coord space
# clip (NDC) -> screen (2D) : coord in 2D screen


class RendererMesh:
    """Renderer for Mesh visual using Matplotlib."""

    @staticmethod
    def render(
        renderer: MatplotlibRenderer,
        viewport: Viewport,
        mesh: Mesh,
        model_matrix: TransBuf,
        camera: Camera,
    ) -> list[matplotlib.artist.Artist]:

        # =============================================================================
        # sanity checks
        # =============================================================================

        assert mesh.geometry.indices is not None, "The mesh geometry must have face indices to be rendered"
        assert mesh.geometry.uvs is not None, "The mesh geometry must have texture coordinates to be rendered"

        # =============================================================================
        # Transform vertices with MVP matrix
        # =============================================================================

        vertices_buffer = TransBufUtils.to_buffer(mesh.geometry.get_vertices())
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

        # vertices_world = vertices_3d_transformed

        # =============================================================================
        # Extract geometry and material
        # =============================================================================

        geometry = mesh.geometry
        material = mesh.material
        faces_uvs = mesh.geometry.uvs[geometry.indices]

        # =============================================================================
        # Compute the world space faces_vertices
        # =============================================================================

        # Get the full transform matrix for the mesh
        # world_matrix = mesh.get_world_matrix()
        # vertices_world = GeometryUtils.apply_transform(geometry.vertices, world_matrix)

        # build the faces vertices and uvs arrays
        # faces_vertices_world = vertices_world[geometry.indices]

        # =============================================================================
        # Compute the NDC faces_vertices
        # =============================================================================

        # Get the full transform matrix for the mesh
        # mvp_matrix = TransformUtils.compute_mvp_matrix(camera, mesh)
        # vertices_ndc, vertices_clip = GeometryUtils.apply_mvp_matrix(geometry.vertices, mvp_matrix)

        vertices_ndc = vertices_3d_transformed

        # build the faces vertices and uvs arrays
        faces_vertices_ndc = vertices_ndc[geometry.indices]

        # =============================================================================
        # Switch vertices to 2d
        # =============================================================================

        # drop z for 2D rendering
        faces_vertices_2d = faces_vertices_ndc[..., :2]

        # =============================================================================
        # Render the mesh using the appropriate material
        # =============================================================================

        if isinstance(mesh.material, MeshBasicMaterial):
            from .matplotlib_renderer_mesh_basic import RendererMeshBasicMaterial

            changed_artists = RendererMeshBasicMaterial.render(
                renderer=renderer,
                viewport=viewport,
                mesh=mesh,
                camera=camera,
                faces_vertices_ndc=faces_vertices_ndc,
                faces_vertices_2d=faces_vertices_2d,
            )
        # elif isinstance(mesh.material, MeshNormalMaterial):
        #     from .renderer_mesh_normal_material import RendererMeshNormalMaterial

        #     changed_artists = RendererMeshNormalMaterial.render(
        #         renderer=renderer,
        #         mesh=mesh,
        #         camera=camera,
        #         faces_vertices_world=faces_vertices_world,
        #         faces_vertices_ndc=faces_vertices_ndc,
        #         faces_vertices_2d=faces_vertices_2d,
        #     )
        # elif isinstance(mesh.material, MeshDepthMaterial):
        #     from .renderer_mesh_depth_material import RendererMeshDepthMaterial

        #     changed_artists = RendererMeshDepthMaterial.render(
        #         renderer=renderer,
        #         mesh=mesh,
        #         camera=camera,
        #         faces_vertices_ndc=faces_vertices_ndc,
        #         faces_vertices_2d=faces_vertices_2d,
        #     )
        # elif isinstance(mesh.material, MeshPhongMaterial):
        #     from .renderer_mesh_phong_material import RendererMeshPhongMaterial

        #     changed_artists = RendererMeshPhongMaterial.render(
        #         renderer=renderer,
        #         camera=camera,
        #         mesh=mesh,
        #         faces_vertices_world=faces_vertices_world,
        #         faces_vertices_ndc=faces_vertices_ndc,
        #         faces_vertices_2d=faces_vertices_2d,
        #     )
        # elif isinstance(mesh.material, MeshTexturedMaterial):
        #     from .renderer_mesh_textured_material import RendererMeshTexturedMaterial

        #     changed_artists = RendererMeshTexturedMaterial.render(
        #         renderer=renderer,
        #         mesh=mesh,
        #         camera=camera,
        #         faces_vertices_world=faces_vertices_world,
        #         faces_vertices_2d=faces_vertices_2d,
        #         faces_uvs=faces_uvs,
        #     )
        else:
            raise ValueError(f"Unsupported material type: {type(mesh.material)}")
        return changed_artists
