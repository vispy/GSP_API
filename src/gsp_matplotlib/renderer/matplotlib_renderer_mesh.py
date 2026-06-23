"""Matplotlib renderer for Mesh objects."""

# pip imports
import typing
import matplotlib.collections
import matplotlib.artist
import numpy as np

# local imports
from gsp.core.camera import Camera
from gsp.core.viewport import Viewport
from gsp.materials.mesh_basic_material import MeshBasicMaterial
from gsp.materials.mesh_normal_material import MeshNormalMaterial
from gsp.materials.mesh_depth_material import MeshDepthMaterial
from gsp.materials.mesh_phong_material import MeshPhongMaterial
from gsp.materials.mesh_textured_material import MeshTexturedMaterial
from gsp.utils.math_utils import MathUtils
from gsp.visuals.mesh import Mesh
from gsp.utils.transbuf_utils import TransBufUtils
from gsp.types.transbuf import TransBuf
from .matplotlib_renderer import MatplotlibRenderer
from .matplotlib_renderer_mesh_basic import RendererMeshBasic
from .matplotlib_renderer_mesh_normal import RendererMeshNormal
from .matplotlib_renderer_mesh_depth import RendererMeshDepth
from .matplotlib_renderer_mesh_phong import RendererMeshPhong
from .matplotlib_renderer_mesh_textured import RendererMeshTextured
from ..extra.bufferx import Bufferx
from ..utils.renderer_utils import RendererUtils


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
        mesh_geometry = mesh.get_geometry()
        mesh_material = mesh.get_material()

        # =============================================================================
        # Resolve buffers to numpy
        # =============================================================================

        vertices_buffer = TransBufUtils.to_buffer(mesh_geometry.get_positions())
        geometry_indices_buffer = TransBufUtils.to_buffer(mesh_geometry.get_indices())
        model_matrix_buffer = TransBufUtils.to_buffer(model_matrix)
        view_matrix_buffer = TransBufUtils.to_buffer(camera.get_view_matrix())
        projection_matrix_buffer = TransBufUtils.to_buffer(camera.get_projection_matrix())

        vertices_numpy = Bufferx.to_numpy(vertices_buffer)
        geometry_indices_numpy = Bufferx.to_numpy(geometry_indices_buffer).flatten().reshape(-1, 3)  # (face_count, 3)
        model_matrix_numpy = Bufferx.to_numpy(model_matrix_buffer).squeeze()
        view_matrix_numpy = Bufferx.to_numpy(view_matrix_buffer).squeeze()
        projection_matrix_numpy = Bufferx.to_numpy(projection_matrix_buffer).squeeze()

        # =============================================================================
        # Sanity checks attributes buffers
        # =============================================================================

        Mesh.sanity_check_attributes_buffer(mesh_geometry, mesh_material)

        face_count = len(geometry_indices_numpy)
        vertex_count = len(vertices_numpy)

        # =============================================================================
        # Compute MVP-transformed and view-space vertices
        # =============================================================================

        mvp_matrix = MathUtils.compute_mvp_matrix(model_matrix_numpy, view_matrix_numpy, projection_matrix_numpy)
        _, vertices_ndc = MathUtils.apply_transform_matrix(vertices_numpy, mvp_matrix)
        faces_vertices_ndc = vertices_ndc[geometry_indices_numpy].reshape(-1, 3, 3)  # (face_count, 3, 3)
        # 2d in screen space (drop z) — used for sort/cull and final PolyCollection verts
        faces_vertices_2d = faces_vertices_ndc[..., :2]  # (face_count, 3, 2)

        # view-space vertices needed by MeshNormalMaterial; cheap to compute even when unused
        view_model_matrix = view_matrix_numpy @ model_matrix_numpy
        vertices_view_numpy, _ = MathUtils.apply_transform_matrix(vertices_numpy, view_model_matrix)

        # world-space vertices and camera position needed by MeshPhongMaterial; cheap to compute even when unused
        vertices_world_numpy, _ = MathUtils.apply_transform_matrix(vertices_numpy, model_matrix_numpy)
        camera_position_world = (np.linalg.inv(view_matrix_numpy) @ np.array([0.0, 0.0, 0.0, 1.0]))[:3]

        # sanity checks on derived shapes
        assert faces_vertices_ndc.shape == (face_count, 3, 3), f"Expected faces_vertices_ndc shape {(face_count, 3, 3)}, got {faces_vertices_ndc.shape}"
        assert faces_vertices_2d.shape == (face_count, 3, 2), f"Expected faces_vertices_2d shape {(face_count, 3, 2)}, got {faces_vertices_2d.shape}"

        # =============================================================================
        # Textured material has its own render path (per-face AxesImages, not PolyCollection)
        # =============================================================================

        if isinstance(mesh_material, MeshTexturedMaterial):
            return RendererMeshTextured.render(
                renderer,
                viewport,
                mesh,
                geometry_indices_numpy,
                vertices_world_numpy,
                faces_vertices_ndc,
                faces_vertices_2d,
                model_matrix_numpy,
                camera_position_world,
                vertex_count,
                face_count,
            )

        # =============================================================================
        # Dispatch to per-material attribute computation
        # =============================================================================

        if isinstance(mesh_material, MeshBasicMaterial):
            face_colors_numpy, material_edge_colors_numpy, material_edge_widths_numpy = RendererMeshBasic.compute_attributes(
                mesh, geometry_indices_numpy, vertices_view_numpy, faces_vertices_ndc, projection_matrix_numpy, vertex_count, face_count,
            )
        elif isinstance(mesh_material, MeshNormalMaterial):
            face_colors_numpy, material_edge_colors_numpy, material_edge_widths_numpy = RendererMeshNormal.compute_attributes(
                mesh, geometry_indices_numpy, vertices_view_numpy, faces_vertices_ndc, projection_matrix_numpy, vertex_count, face_count,
            )
        elif isinstance(mesh_material, MeshDepthMaterial):
            face_colors_numpy, material_edge_colors_numpy, material_edge_widths_numpy = RendererMeshDepth.compute_attributes(
                mesh, geometry_indices_numpy, vertices_view_numpy, faces_vertices_ndc, projection_matrix_numpy, vertex_count, face_count,
            )
        elif isinstance(mesh_material, MeshPhongMaterial):
            face_colors_numpy, material_edge_colors_numpy, material_edge_widths_numpy = RendererMeshPhong.compute_attributes(
                mesh, geometry_indices_numpy, vertices_view_numpy, vertices_world_numpy, faces_vertices_ndc,
                projection_matrix_numpy, model_matrix_numpy, camera_position_world, vertex_count, face_count,
            )
        else:
            raise NotImplementedError(f"Mesh material {type(mesh_material)} not supported")

        material_face_sorting = mesh_material.get_face_sorting()
        material_face_culling = mesh_material.get_face_culling()

        # =============================================================================
        # Honor material.face_sorting
        # =============================================================================

        # Sort polygons by depth (painter's algorithm)
        # - faces are sorted based on their depth (z) in NDC space within a single artist
        # - this artist.set_zorder() is set based on the distance from the camera to the Object3D position
        # - so possible conflict between faces of different objects
        if material_face_sorting:
            faces_depth = RendererUtils.compute_face_depths_ndc(faces_vertices_ndc)
            # NDC z runs from -1 (near) to +1 (far); painter's algorithm draws farthest first
            # so nearer faces are painted on top — sort descending by z.
            depth_sorted_indices = np.argsort(-faces_depth)
            # ALL per-face arrays MUST be reordered with the same indices to keep them in sync
            faces_vertices_2d = faces_vertices_2d[depth_sorted_indices]
            face_colors_numpy = face_colors_numpy[depth_sorted_indices]
            material_edge_colors_numpy = material_edge_colors_numpy[depth_sorted_indices]
            material_edge_widths_numpy = material_edge_widths_numpy[depth_sorted_indices]

        # =============================================================================
        # honor material.face_culling
        # =============================================================================

        faces_visible = RendererUtils.compute_faces_visible(faces_vertices_2d, material_face_culling)

        # ALL per-face arrays MUST be filtered with the same mask to keep them in sync
        faces_vertices_2d = faces_vertices_2d[faces_visible]
        face_colors_numpy = face_colors_numpy[faces_visible]
        material_edge_colors_numpy = material_edge_colors_numpy[faces_visible]
        material_edge_widths_numpy = material_edge_widths_numpy[faces_visible]

        # =============================================================================
        # Create artists if needed
        # =============================================================================
        if mesh.get_uuid() not in renderer._artists:
            mpl_poly_collection = matplotlib.collections.PolyCollection([], clip_on=False, snap=False)
            mpl_poly_collection.set_visible(False)  # hide until properly positioned and sized
            renderer._artists[mesh.get_uuid()] = mpl_poly_collection
            axes = renderer.get_mpl_axes_for_viewport(viewport)
            axes.add_artist(mpl_poly_collection)

        # =============================================================================
        # Get the mpl_artist
        # =============================================================================

        mpl_poly_collection = typing.cast(matplotlib.collections.PolyCollection, renderer._artists[mesh.get_uuid()])
        mpl_poly_collection.set_visible(True)

        # =============================================================================
        # Update all the artists
        # =============================================================================

        # update the PolyCollection with the new patches
        mpl_poly_collection.set_verts(typing.cast(list[typing.Any], faces_vertices_2d))
        mpl_poly_collection.set_facecolor(typing.cast(list[typing.Any], face_colors_numpy))
        mpl_poly_collection.set_edgecolor(typing.cast(list[typing.Any], material_edge_colors_numpy))
        mpl_poly_collection.set_linewidth(typing.cast(list[typing.Any], material_edge_widths_numpy))

        return [mpl_poly_collection]
