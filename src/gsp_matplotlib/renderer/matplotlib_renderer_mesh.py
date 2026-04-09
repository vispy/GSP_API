"""Matplotlib renderer for Mesh objects."""

# pip imports
import typing
import matplotlib.collections
import matplotlib.artist
import numpy as np

# local imports
from gsp.core.camera import Camera
from gsp.core.viewport import Viewport
from gsp.constants import Constants
from gsp.materials.mesh_material import MeshMaterial
from gsp.materials.mesh_basic_material import MeshBasicMaterial
from gsp.utils.math_utils import MathUtils
from gsp.visuals.mesh import Mesh
from gsp.utils.transbuf_utils import TransBufUtils
from gsp.types.transbuf import TransBuf
from .matplotlib_renderer import MatplotlibRenderer
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
        mesh_material: MeshBasicMaterial = typing.cast(MeshBasicMaterial, mesh.get_material())  # TODO support other MeshMaterial types

        # =============================================================================
        # Transform vertices with MVP matrix
        # =============================================================================

        vertices_buffer = TransBufUtils.to_buffer(mesh_geometry.get_positions())
        model_matrix_buffer = TransBufUtils.to_buffer(model_matrix)
        view_matrix_buffer = TransBufUtils.to_buffer(camera.get_view_matrix())
        projection_matrix_buffer = TransBufUtils.to_buffer(camera.get_projection_matrix())

        # convert all necessary buffers to numpy arrays
        vertices_numpy = Bufferx.to_numpy(vertices_buffer)
        model_matrix_numpy = Bufferx.to_numpy(model_matrix_buffer).squeeze()
        view_matrix_numpy = Bufferx.to_numpy(view_matrix_buffer).squeeze()
        projection_matrix_numpy = Bufferx.to_numpy(projection_matrix_buffer).squeeze()

        # =============================================================================
        #
        # =============================================================================

        geometry_indices_buffer = TransBufUtils.to_buffer(mesh_geometry.get_indices())
        geometry_uvs_buffer = TransBufUtils.to_buffer(mesh_geometry.get_uvs())
        geometry_normals_buffer = TransBufUtils.to_buffer(mesh_geometry.get_normals())
        material_colors_buffer = TransBufUtils.to_buffer(mesh_material.get_colors())
        material_edge_colors_buffer = TransBufUtils.to_buffer(mesh_material.get_edge_colors())
        material_edge_widths_buffer = TransBufUtils.to_buffer(mesh_material.get_edge_widths())

        # Convert buffers to numpy arrays
        geometry_indices_numpy = Bufferx.to_numpy(geometry_indices_buffer).reshape(-1, 3)  # shape(face_count, vertices_per_face) - shape(face_count, 3)
        geometry_uvs_numpy = Bufferx.to_numpy(geometry_uvs_buffer)
        geometry_normals_numpy = Bufferx.to_numpy(geometry_normals_buffer)
        material_colors_numpy = Bufferx.to_numpy(material_colors_buffer) / 255.0  # convert from 0-255 to 0-1 range for matplotlib

        # TODO take them from the material
        material_edge_color = np.array([Constants.Color.black] * len(geometry_indices_numpy)) / 255.0  # convert from 0-255 to 0-1 range for matplotlib
        material_edge_widths = np.array([0.5] * len(geometry_indices_numpy))

        # =============================================================================
        # Sanity checks attributes buffers
        # =============================================================================

        Mesh.sanity_check_attributes_buffer(
            mesh.get_geometry(),
            mesh.get_material(),
        )

        # =============================================================================
        # Compute the world space faces_vertices
        # =============================================================================

        # Get the full transform matrix for the mesh
        vertices_world, _ = MathUtils.apply_transform_matrix(vertices_numpy, model_matrix_numpy)

        # build the faces vertices and uvs arrays
        faces_vertices_world = vertices_world[geometry_indices_numpy]

        # =============================================================================
        # Compute the faces_uvs
        # =============================================================================

        faces_uvs_numpy = geometry_uvs_numpy[geometry_indices_numpy]

        # =============================================================================
        # Compute the NDC faces_vertices
        # =============================================================================

        # Get the full transform matrix for the mesh
        mvp_matrix = MathUtils.compute_mvp_matrix(model_matrix_numpy, view_matrix_numpy, projection_matrix_numpy)
        vertices_clip, vertices_ndc = MathUtils.apply_transform_matrix(vertices_numpy, mvp_matrix)

        # build the faces vertices and uvs arrays
        faces_vertices_ndc = vertices_ndc[geometry_indices_numpy].reshape(-1, 3, 3)  # shape(face_count, vertices_per_face, xyz) - shape(face_count, 3, 3)

        # =============================================================================
        # Switch vertices to 2d
        # =============================================================================

        # drop z for 2D rendering
        faces_vertices_2d = faces_vertices_ndc[..., :2]  # shape(face_count, vertices_per_face, xy) - shape(face_count, 3, 2)

        # =============================================================================
        # Render the mesh using the appropriate material
        # =============================================================================

        # =============================================================================
        # Sanity checks
        # =============================================================================

        # faces_vertices_ndc: (n_faces, 3, 3) array of the 3D vertices of each face in NDC space
        # faces_vertices_2d: (n_faces, 3, 2) array of the 2D vertices of each face in screen space
        # faces_uvs: (n_faces, 3, 2) array of the UV coordinates of each face

        assert isinstance(mesh_material, MeshMaterial), f"Expected material to be a MeshMaterial, got {type(mesh_material)}"
        assert faces_vertices_ndc.shape == (
            len(geometry_indices_numpy),
            3,
            3,
        ), f"Expected faces_vertices_ndc to have shape {(len(geometry_indices_numpy), 3, 3)}, got {faces_vertices_ndc.shape}"
        assert faces_vertices_2d.shape == (
            len(geometry_indices_numpy),
            3,
            2,
        ), f"Expected faces_vertices_2d to have shape {(len(geometry_indices_numpy), 3, 2)}, got {faces_vertices_2d.shape}"
        assert len(faces_vertices_2d) == len(
            geometry_indices_numpy
        ), f"Expected faces_vertices_2d to have {len(geometry_indices_numpy)} faces, got {len(faces_vertices_2d)}"

        # =============================================================================
        #
        # =============================================================================

        material_face_sorting = mesh_material.get_face_sorting()
        material_face_culling = mesh_material.get_face_culling()

        # =============================================================================
        # Honor material.face_sorting
        # =============================================================================

        # Sort polygons by depth (painter's algorithm)
        # - faces are sorted based on their depth (z) in camera space within a single artist
        # - this artist.set_zorder() is set based on the distance from the camera to the Object3D position
        # - so possible conflict between faces of different objects
        # - CAUTION: here reorder ALL arrays you use below to keep them in sync
        if material_face_sorting:
            # compute the depth of each face as the mean z value of its vertices
            faces_depth = faces_vertices_ndc[:, :, 2].mean(axis=1)
            # get the sorting indices (from farthest to nearest)
            depth_sorted_indices = np.argsort(faces_depth)
            # apply the sorting to faces_vertices and faces_hidden
            # CAUTION: here reorder ALL arrays you use below to keep them in sync
            faces_vertices_2d = faces_vertices_2d[depth_sorted_indices]

            # FIXME make it happens
            # # ALL attributes used below MUST be reordered with the same depth_sorted_indices to keep them in sync
            # material_colors_numpy = material_colors_numpy[depth_sorted_indices]
            # material_edge_color = material_edge_color[depth_sorted_indices]

        # =============================================================================
        # honor material.face_culling
        # =============================================================================

        faces_visible = RendererUtils.compute_faces_visible(faces_vertices_2d, material_face_culling)
        # print(f"faces_visible: {faces_visible.sum()}/{len(faces_visible)}")

        # remove hidden faces
        faces_vertices_2d = faces_vertices_2d[faces_visible]

        # FIXME make it happens
        # # ALL attributes used below MUST filtered with the same faces_visible mask to keep them in sync
        # material_colors_numpy = material_colors_numpy[faces_visible]
        # material_edge_color = material_edge_color[faces_visible]

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

        # # =============================================================================
        # # do z-ordering based on distance to camera
        # # =============================================================================

        # # compute and set zorder on our single artist
        # RendererUtils.update_single_artist_zorder(camera, mesh, mpl_poly_collection)

        # =============================================================================
        # Update all the artists
        # =============================================================================

        # update the PathCollection with the new patches
        mpl_poly_collection.set_verts(typing.cast(list, faces_vertices_2d))
        mpl_poly_collection.set_facecolor(typing.cast(list, material_colors_numpy))

        mpl_poly_collection.set_edgecolor(typing.cast(list, material_edge_color))
        mpl_poly_collection.set_linewidth(typing.cast(list, material_edge_widths))

        return [mpl_poly_collection]
