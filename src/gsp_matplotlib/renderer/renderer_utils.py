# pip imports
import matplotlib.artist
import numpy as np

# local imports
from gsp.core import Camera

# from ..core import Object3D
from gsp.constants import Constants

# from ..lights import Light, DirectionalLight, PointLight, AmbientLight


class RendererUtils:
    """Utility functions for renderers."""

    # @staticmethod
    # def update_single_artist_zorder(camera: Camera, object3d: Object3D, artist: matplotlib.artist.Artist):
    #     """Update the zorder of a single artist based on the distance from the camera to the Object3D position.
    #     - larger distance -> smaller zorder (drawn first)

    #     NOTE: work only if the rendering of the object3d submitted a single artist.
    #     if it got multiple artists, it will need to set the zorder itself.
    #     """
    #     # compute distance from camera to object3d
    #     camera_position = camera.get_world_position()
    #     object_position = object3d.get_world_position()
    #     distance_to_camera = ((camera_position - object_position) ** 2).sum() ** 0.5

    #     # set zorder based on distance (larger distance -> smaller zorder)
    #     object_zorder = -distance_to_camera

    #     # set the artist zorder
    #     artist.set_zorder(object_zorder)

    @staticmethod
    def compute_faces_centroids(faces_vertices_world: np.ndarray) -> np.ndarray:
        """Compute the face centroids.

        Args:
            faces_vertices_world (np.ndarray): shape = [num_faces, 3, 3] in world space
        Returns:
            np.ndarray: shape = [num_faces, 3] in world space
        """
        faces_centroids = np.mean(faces_vertices_world, axis=1)
        return faces_centroids

    @staticmethod
    def compute_faces_normal_unit(faces_vertices_world: np.ndarray) -> np.ndarray:
        """Compute the face normals for lighting.

        Args:
            faces_vertices_world (np.ndarray): shape = [num_faces, 3, 3] in world space
        Returns:
            np.ndarray: shape = [num_faces, 3] unit vectors in world space
        """
        # =============================================================================
        # Compute face normals - needed for lighting and back-face culling
        # =============================================================================
        faces_normals = np.cross(
            faces_vertices_world[:, 2] - faces_vertices_world[:, 0],
            faces_vertices_world[:, 1] - faces_vertices_world[:, 0],
        )
        # FIXME this will trigger exception on degenerated faces...
        faces_normals_unit = faces_normals / np.linalg.norm(faces_normals, axis=1).reshape(len(faces_normals), 1)

        return faces_normals_unit

    @staticmethod
    def compute_faces_visible(faces_vertices_2d: np.ndarray, face_culling: Constants.FaceCulling) -> np.ndarray:
        """Compute which faces are visible based on their normals and the camera position.

        Returns:
            np.ndarray: A boolean array indicating which faces are visible.
        """
        # For each face, compute the cross product of the edges in 2D
        # - if the z component is positive, the face is oriented counter-clockwise
        # - if the z component is negative, the face is oriented clockwise
        # - if the z component is zero, the face is degenerated (line or point)
        faces_edges_2d_a = faces_vertices_2d[:, 1] - faces_vertices_2d[:, 0]
        faces_edges_2d_b = faces_vertices_2d[:, 2] - faces_vertices_2d[:, 0]
        faces_cross_z = faces_edges_2d_a[:, 0] * faces_edges_2d_b[:, 1] - faces_edges_2d_a[:, 1] * faces_edges_2d_b[:, 0]
        # this is the threshold below which a face is considered degenerated and trigger exception when inverting matrix
        faces_cross_threshold = 1e-6
        if face_culling == Constants.FaceCulling.FrontSide:
            faces_visible = faces_cross_z <= -faces_cross_threshold
        elif face_culling == Constants.FaceCulling.BackSide:
            faces_visible = faces_cross_z >= faces_cross_threshold
        elif face_culling == Constants.FaceCulling.BothSides:
            # If the face is degenerated (line or point), it is not visible
            faces_visible = np.abs(faces_cross_z) > faces_cross_threshold
        else:
            raise ValueError(f"Unknown face culling mode: {face_culling}")

        # print(f"faces_visible: {faces_visible.sum()}/{len(faces_visible)}")
        return faces_visible

    # # =============================================================================
    # # Flat shading
    # # =============================================================================

    # @staticmethod
    # def shade_faces_flat(
    #     camera: Camera,
    #     material_color: np.ndarray,
    #     material_shininess: float,
    #     faces_normals_unit: np.ndarray,
    #     faces_centroids_world: np.ndarray,
    #     lights: list[Light],
    # ) -> np.ndarray:
    #     """
    #     Flat shading per face using isinstance for light types.
    #     Diffuse + ambient only, no specular.

    #     normals_world: [F, 3]  -> unit normal per face
    #     face_centroids_world: [F, 3] -> centroid per face
    #     lights: list of light objects (AmbientLight, DirectionalLight, PointLight)
    #     base_color: np.array([3]) RGB
    #     """

    #     # sanity checks - check np.ndarray's
    #     assert faces_normals_unit.ndim == 2 and faces_normals_unit.shape[1] == 3, f"normals_world should be of shape [F, 3], got {faces_normals_unit.shape}"
    #     assert (
    #         faces_centroids_world.ndim == 2 and faces_centroids_world.shape[1] == 3
    #     ), f"face_centroids_world should be of shape [F, 3], got {faces_centroids_world.shape}"
    #     assert material_color.shape == (3,) or material_color.shape == (4,), f"material_color should be of shape (3,) or (4,), got {material_color.shape}"

    #     num_faces = faces_normals_unit.shape[0]
    #     shaded = np.zeros((num_faces, 3), dtype=np.float32)

    #     base_color_rgb = np.array(material_color[:3], dtype=np.float32)

    #     # --- Ambient lights
    #     for light in lights:
    #         if isinstance(light, AmbientLight):
    #             light_color_rgb = np.array(light.color[:3], dtype=np.float32)
    #             shaded += base_color_rgb * light_color_rgb * light.intensity

    #     # --- Directional and Point lights
    #     for light in lights:
    #         if isinstance(light, DirectionalLight):
    #             # Light direction toward scene origin (or target)
    #             target = np.array([0, 0, 0], dtype=np.float32)
    #             L = target - light.get_world_position()
    #             L = L / np.linalg.norm(L)
    #             L_dir = np.tile(L, (num_faces, 1))
    #             attenuation = 1.0

    #         elif isinstance(light, PointLight):
    #             # Vector from face centroid to point light
    #             L_dir = light.get_world_position() - faces_centroids_world
    #             dist = np.linalg.norm(L_dir, axis=1, keepdims=True) + 1e-6
    #             L_dir = L_dir / dist
    #             attenuation = 1.0 / (dist * dist)

    #         else:
    #             continue

    #         # --- Diffuse Lambert
    #         ndotl = np.clip(np.sum(faces_normals_unit * L_dir, axis=1, keepdims=True), 0, 1)
    #         light_color_rgb = np.array(light.color[:3], dtype=np.float32)
    #         diffuse = base_color_rgb * light_color_rgb * light.intensity * ndotl * attenuation
    #         shaded += diffuse

    #         # --- Specular Phong
    #         V = camera.get_world_position() - faces_centroids_world
    #         V = V / (np.linalg.norm(V, axis=1, keepdims=True) + 1e-6)
    #         R = 2 * ndotl * faces_normals_unit - L_dir
    #         R = R / (np.linalg.norm(R, axis=1, keepdims=True) + 1e-6)
    #         spec_angle = np.clip(np.sum(R * V, axis=1, keepdims=True), 0, 1)
    #         specular = light_color_rgb * (spec_angle**material_shininess) * attenuation
    #         shaded += specular

    #     return np.clip(shaded, 0, 1)
