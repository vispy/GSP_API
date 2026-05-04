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
        mesh_material = mesh.get_material()
        assert isinstance(mesh_material, MeshBasicMaterial), f"Expected material to be a MeshBasicMaterial, got {type(mesh_material)}"  # TODO support other MeshMaterial types

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
        # Geometry/material attributes
        # =============================================================================

        geometry_indices_buffer = TransBufUtils.to_buffer(mesh_geometry.get_indices())
        material_colors_buffer = TransBufUtils.to_buffer(mesh_material.get_colors())
        material_edge_colors_buffer = TransBufUtils.to_buffer(mesh_material.get_edge_colors())
        material_edge_widths_buffer = TransBufUtils.to_buffer(mesh_material.get_edge_widths())

        # Convert buffers to numpy arrays
        geometry_indices_numpy = Bufferx.to_numpy(geometry_indices_buffer).flatten().reshape(-1, 3)  # shape(face_count, 3)
        material_colors_numpy = Bufferx.to_numpy(material_colors_buffer) / 255.0  # convert from 0-255 to 0-1 range for matplotlib
        material_edge_colors_numpy = Bufferx.to_numpy(material_edge_colors_buffer) / 255.0
        material_edge_widths_numpy = Bufferx.to_numpy(material_edge_widths_buffer).flatten()

        # matplotlib's PolyCollection takes one color/width per face. Material attributes may be
        # per-vertex (length == vertex_count) or per-mesh (length == 1) — broadcast/index to per-face.
        face_count = len(geometry_indices_numpy)
        vertex_count = len(vertices_numpy)

        def _to_per_face(array: np.ndarray) -> np.ndarray:
            if array.shape[0] == face_count:
                return array
            if array.shape[0] == vertex_count:
                return array[geometry_indices_numpy[:, 0]]
            if array.shape[0] == 1:
                return np.broadcast_to(array, (face_count,) + array.shape[1:]).copy()
            raise ValueError(f"unexpected attribute length {array.shape[0]}; expected 1, face_count={face_count}, or vertex_count={vertex_count}")

        material_colors_numpy = _to_per_face(material_colors_numpy)
        material_edge_colors_numpy = _to_per_face(material_edge_colors_numpy)
        material_edge_widths_numpy = _to_per_face(material_edge_widths_numpy)

        # =============================================================================
        # Sanity checks attributes buffers
        # =============================================================================

        Mesh.sanity_check_attributes_buffer(
            mesh.get_geometry(),
            mesh.get_material(),
        )

        # =============================================================================
        # Compute the NDC faces_vertices
        # =============================================================================

        mvp_matrix = MathUtils.compute_mvp_matrix(model_matrix_numpy, view_matrix_numpy, projection_matrix_numpy)
        _, vertices_ndc = MathUtils.apply_transform_matrix(vertices_numpy, mvp_matrix)

        faces_vertices_ndc = vertices_ndc[geometry_indices_numpy].reshape(-1, 3, 3)  # shape(face_count, 3, xyz)

        # =============================================================================
        # Switch vertices to 2d
        # =============================================================================

        # drop z for 2D rendering
        faces_vertices_2d = faces_vertices_ndc[..., :2]  # shape(face_count, vertices_per_face, xy) - shape(face_count, 3, 2)

        # =============================================================================
        # Sanity checks
        # =============================================================================

        # faces_vertices_ndc: (face_count, 3, 3) — 3D vertices of each face in NDC space
        # faces_vertices_2d:  (face_count, 3, 2) — 2D vertices of each face in screen space
        assert faces_vertices_ndc.shape == (face_count, 3, 3), f"Expected faces_vertices_ndc shape {(face_count, 3, 3)}, got {faces_vertices_ndc.shape}"
        assert faces_vertices_2d.shape == (face_count, 3, 2), f"Expected faces_vertices_2d shape {(face_count, 3, 2)}, got {faces_vertices_2d.shape}"

        # =============================================================================
        #
        # =============================================================================

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
            # compute the depth of each face as the mean z value of its vertices
            faces_depth = faces_vertices_ndc[:, :, 2].mean(axis=1)
            # NDC z runs from -1 (near) to +1 (far); painter's algorithm draws farthest first
            # so nearer faces are painted on top — sort descending by z.
            depth_sorted_indices = np.argsort(-faces_depth)
            # ALL per-face arrays MUST be reordered with the same indices to keep them in sync
            faces_vertices_2d = faces_vertices_2d[depth_sorted_indices]
            material_colors_numpy = material_colors_numpy[depth_sorted_indices]
            material_edge_colors_numpy = material_edge_colors_numpy[depth_sorted_indices]
            material_edge_widths_numpy = material_edge_widths_numpy[depth_sorted_indices]

        # =============================================================================
        # honor material.face_culling
        # =============================================================================

        faces_visible = RendererUtils.compute_faces_visible(faces_vertices_2d, material_face_culling)

        # ALL per-face arrays MUST be filtered with the same mask to keep them in sync
        faces_vertices_2d = faces_vertices_2d[faces_visible]
        material_colors_numpy = material_colors_numpy[faces_visible]
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

        # # =============================================================================
        # # do z-ordering based on distance to camera
        # # =============================================================================

        # # compute and set zorder on our single artist
        # RendererUtils.update_single_artist_zorder(camera, mesh, mpl_poly_collection)

        # =============================================================================
        # Update all the artists
        # =============================================================================

        # update the PolyCollection with the new patches
        mpl_poly_collection.set_verts(typing.cast(list, faces_vertices_2d))
        mpl_poly_collection.set_facecolor(typing.cast(list, material_colors_numpy))
        mpl_poly_collection.set_edgecolor(typing.cast(list, material_edge_colors_numpy))
        mpl_poly_collection.set_linewidth(typing.cast(list, material_edge_widths_numpy))

        return [mpl_poly_collection]
