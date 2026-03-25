# stdlib imports
import typing

# pip imports
import matplotlib.artist
import matplotlib.collections
import numpy as np


# local imports
from gsp.materials import MeshNormalMaterial
from gsp.visuals.mesh import Mesh
from .matplotlib_renderer import MatplotlibRenderer
from gsp.core.camera import Camera
from gsp.core.viewport import Viewport
from .renderer_utils import RendererUtils


class RendererMeshNormalMaterial:
    """A class responsible for rendering Mesh visuals with MeshNormalMaterial using Matplotlib."""

    @staticmethod
    def render(
        renderer: MatplotlibRenderer,
        viewport: Viewport,
        mesh: Mesh,
        camera: Camera,
        faces_vertices_world: np.ndarray,
        faces_vertices_ndc: np.ndarray,
        faces_vertices_2d: np.ndarray,
    ) -> list[matplotlib.artist.Artist]:
        geometry = mesh.geometry
        material = typing.cast(MeshNormalMaterial, mesh.material)

        # =============================================================================
        # Sanity checks
        # =============================================================================

        # faces_vertices_world: (n_faces, 3, 3) array of the 3D vertices of each face in world space
        # faces_vertices_2d: (n_faces, 3, 2) array of the 2D vertices of each face in screen space
        # faces_uvs: (n_faces, 3, 2) array of the UV coordinates of each face

        # sanity check
        assert isinstance(material, MeshNormalMaterial), f"Expected material to be a MeshNormalMaterial, got {type(material)}"
        assert faces_vertices_ndc.shape == (
            len(geometry.indices),
            3,
            3,
        ), f"Expected faces_vertices_world to have shape {(len(geometry.indices), 3, 3)}, got {faces_vertices_ndc.shape}"
        assert faces_vertices_2d.shape == (
            len(geometry.indices),
            3,
            2,
        ), f"Expected faces_vertices_2d to have shape {(len(geometry.indices), 3, 2)}, got {faces_vertices_2d.shape}"
        assert len(faces_vertices_2d) == len(
            geometry.indices
        ), f"Expected faces_vertices_2d to have {len(geometry.indices)} faces, got {len(faces_vertices_2d)}"

        # =============================================================================
        # Computes faces_color
        # =============================================================================

        faces_normals_unit = RendererUtils.compute_faces_normal_unit(faces_vertices_world)
        camera_direction = mesh.get_world_position() - camera.get_world_position()
        camera_direction /= np.linalg.norm(camera_direction)
        camera_cosines: np.ndarray = np.cross(faces_normals_unit, camera_direction)
        faces_color = (camera_cosines + 1) / 2

        # =============================================================================
        # Face sorting based on depth
        # =============================================================================

        # Sort polygons by depth (painter's algorithm)
        # - faces are sorted based on their depth (z) in camera space within a single artist
        # - this artist.set_zorder() is set based on the distance from the camera to the Object3D position
        # - so possible conflict between faces of different objects
        # - CAUTION: here reorder ALL arrays you use below to keep them in sync
        if material.face_sorting:
            # compute the depth of each face as the mean z value of its vertices
            faces_depth = faces_vertices_ndc[:, :, 2].mean(axis=1)
            # get the sorting indices (from farthest to nearest)
            depth_sorted_indices = np.argsort(faces_depth)
            # apply the sorting to faces_vertices and faces_hidden
            # CAUTION: here reorder ALL arrays you use below to keep them in sync
            faces_vertices_2d = faces_vertices_2d[depth_sorted_indices]
            faces_color = faces_color[depth_sorted_indices]

        # =============================================================================
        # honor material.face_culling
        # =============================================================================

        faces_visible = RendererUtils.compute_faces_visible(faces_vertices_2d, material.face_culling)

        # remove hidden faces
        faces_vertices_2d = faces_vertices_2d[faces_visible]
        faces_color = faces_color[faces_visible]

        # =============================================================================
        # Create artists if needed
        # =============================================================================
        if mesh.get_uuid() not in renderer._artists:
            axes = renderer.get_mpl_axes_for_viewport(viewport)
            mpl_poly_collection = matplotlib.collections.PolyCollection([], clip_on=False, snap=False)
            mpl_poly_collection.set_visible(False)  # hide until properly positioned and sized
            axes.add_collection(mpl_poly_collection)
            renderer._artists[mesh.get_uuid()] = mpl_poly_collection

        # =============================================================================
        # Get the mpl_artist
        # =============================================================================

        mpl_poly_collection = typing.cast(matplotlib.collections.PolyCollection, renderer._artists[mesh.get_uuid()])
        mpl_poly_collection.set_visible(True)

        # =============================================================================
        # do z-ordering based on distance to camera
        # =============================================================================

        # TODO removed this line during merging
        # # compute and set zorder on our single artist
        # RendererUtils.update_single_artist_zorder(camera, mesh, mpl_poly_collection)

        # =============================================================================
        # Update all the artists
        # =============================================================================

        # update the PathCollection with the new patches
        mpl_poly_collection.set_verts(typing.cast(list, faces_vertices_2d))
        mpl_poly_collection.set_facecolor(typing.cast(list, faces_color))
        mpl_poly_collection.set_edgecolor(typing.cast(list, material.edge_colors))
        mpl_poly_collection.set_linewidth(typing.cast(list, material.edge_widths))

        return [mpl_poly_collection]
