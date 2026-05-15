"""Per-material attribute computation for MeshPhongMaterial."""

# pip imports
from typing import Sequence

import numpy as np

# local imports
from gsp.lights.ambient_light import AmbientLight
from gsp.lights.directional_light import DirectionalLight
from gsp.lights.light import Light
from gsp.lights.point_light import PointLight
from gsp.materials.mesh_phong_material import MeshPhongMaterial
from gsp.types.transbuf import TransBuf
from gsp.utils.math_utils import MathUtils
from gsp.utils.transbuf_utils import TransBufUtils
from gsp.visuals.mesh import Mesh
from ..extra.bufferx import Bufferx
from ..utils.renderer_utils import RendererUtils


class RendererMeshPhong:
    """Compute per-face visual attributes for a Mesh using MeshPhongMaterial."""

    @staticmethod
    def compute_attributes(
        mesh: Mesh,
        geometry_indices_numpy: np.ndarray,
        vertices_view_numpy: np.ndarray,
        vertices_world_numpy: np.ndarray,
        faces_vertices_ndc: np.ndarray,
        projection_matrix_numpy: np.ndarray,
        model_matrix_numpy: np.ndarray,
        camera_position_world: np.ndarray,
        vertex_count: int,
        face_count: int,
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Compute per-face (face_colors, edge_colors, edge_widths) for the given mesh.

        Flat per-face Phong shading in world space. Lights live on the material and
        their positions are in model space; they are transformed to world space here.

        Args:
            mesh (Mesh): The mesh being rendered.
            geometry_indices_numpy (np.ndarray): Triangle indices, shape (face_count, 3).
            vertices_view_numpy (np.ndarray): View-space vertices (unused), shape (vertex_count, 3).
            vertices_world_numpy (np.ndarray): World-space vertices, shape (vertex_count, 3).
            faces_vertices_ndc (np.ndarray): Per-face NDC vertices (unused), shape (face_count, 3, 3).
            projection_matrix_numpy (np.ndarray): Camera projection matrix (unused), shape (4, 4).
            model_matrix_numpy (np.ndarray): Model matrix, shape (4, 4). Used to transform light positions.
            camera_position_world (np.ndarray): Camera position in world space, shape (3,).
            vertex_count (int): Number of vertices.
            face_count (int): Number of faces.

        Returns:
            tuple[np.ndarray, np.ndarray, np.ndarray]: face_colors (face_count, 4),
                edge_colors (face_count, 4), edge_widths (face_count,).
        """
        material = mesh.get_material()
        assert isinstance(material, MeshPhongMaterial), f"Expected MeshPhongMaterial, got {type(material)}"

        lights = material.get_lights()
        shininess = material.get_shininess()

        # Per-face world-space normals and centroids.
        face_normals_world = RendererUtils.compute_face_normals_world(vertices_world_numpy, geometry_indices_numpy)
        faces_vertices_world = vertices_world_numpy[geometry_indices_numpy]  # (face_count, 3, 3)
        face_centroids_world = faces_vertices_world.mean(axis=1)  # (face_count, 3)

        # Material colors broadcast to per-face.
        diffuse_buffer = TransBufUtils.to_buffer(material.get_diffuse_color())
        specular_buffer = TransBufUtils.to_buffer(material.get_specular_color())
        diffuse_numpy = Bufferx.to_numpy(diffuse_buffer)[:, :3] / 255.0  # drop alpha; (N, 3)
        specular_numpy = Bufferx.to_numpy(specular_buffer)[:, :3] / 255.0
        diffuse_per_face = RendererUtils.to_per_face(diffuse_numpy, face_count, vertex_count, geometry_indices_numpy)
        specular_per_face = RendererUtils.to_per_face(specular_numpy, face_count, vertex_count, geometry_indices_numpy)

        face_rgb = RendererMeshPhong.shade_faces_flat(
            diffuse_per_face=diffuse_per_face,
            specular_per_face=specular_per_face,
            shininess=shininess,
            lights=lights,
            face_normals_world=face_normals_world,
            face_centroids_world=face_centroids_world,
            camera_position_world=camera_position_world,
            model_matrix_numpy=model_matrix_numpy,
            face_count=face_count,
        )
        face_alpha = np.ones((face_count, 1), dtype=face_rgb.dtype)
        face_colors_per_face = np.concatenate([face_rgb, face_alpha], axis=1)

        edge_colors_buffer = TransBufUtils.to_buffer(material.get_edge_colors())
        edge_widths_buffer = TransBufUtils.to_buffer(material.get_edge_widths())
        edge_colors_numpy = Bufferx.to_numpy(edge_colors_buffer) / 255.0
        edge_widths_numpy = Bufferx.to_numpy(edge_widths_buffer).flatten()
        edge_colors_per_face = RendererUtils.to_per_face(edge_colors_numpy, face_count, vertex_count, geometry_indices_numpy)
        edge_widths_per_face = RendererUtils.to_per_face(edge_widths_numpy, face_count, vertex_count, geometry_indices_numpy)

        return face_colors_per_face, edge_colors_per_face, edge_widths_per_face

    # =============================================================================
    # Shared flat Phong shading helper (also used by RendererMeshTextured)
    # =============================================================================

    @staticmethod
    def shade_faces_flat(
        diffuse_per_face: np.ndarray,
        specular_per_face: np.ndarray,
        shininess: float,
        lights: Sequence[Light],
        face_normals_world: np.ndarray,
        face_centroids_world: np.ndarray,
        camera_position_world: np.ndarray,
        model_matrix_numpy: np.ndarray,
        face_count: int,
    ) -> np.ndarray:
        """Accumulate per-face RGB shading over a list of lights (Lambert diffuse + Phong specular).

        Args:
            diffuse_per_face (np.ndarray): (face_count, 3) RGB in [0, 1]. Also serves as the ambient base.
            specular_per_face (np.ndarray): (face_count, 3) RGB in [0, 1].
            shininess (float): Phong specular exponent.
            lights (Sequence[Light]): Mix of AmbientLight, DirectionalLight, PointLight.
            face_normals_world (np.ndarray): (face_count, 3) unit normals in world space.
            face_centroids_world (np.ndarray): (face_count, 3) face centroids in world space.
            camera_position_world (np.ndarray): (3,) camera position in world space.
            model_matrix_numpy (np.ndarray): (4, 4) model matrix used to transform light positions.
            face_count (int): Number of faces.

        Returns:
            np.ndarray: (face_count, 3) RGB in [0, 1], clipped.
        """
        # Per-face view direction (toward camera).
        view_dirs = camera_position_world[np.newaxis, :] - face_centroids_world  # (face_count, 3)
        view_dirs = view_dirs / np.maximum(np.linalg.norm(view_dirs, axis=1, keepdims=True), 1e-12)

        face_rgb = np.zeros((face_count, 3), dtype=np.float64)
        for light in lights:
            light_color_rgb = np.asarray(light.get_color(), dtype=np.float64)[:3] / 255.0
            light_intensity = light.get_intensity()
            scaled_light = light_color_rgb * light_intensity  # shape (3,)

            if isinstance(light, AmbientLight):
                face_rgb += diffuse_per_face * scaled_light[np.newaxis, :]
                continue

            # Convention: light_dirs points FROM the face TOWARD the light source,
            # so max(0, normal · light_dirs) is the standard Lambert term.
            if isinstance(light, DirectionalLight):
                light_pos_world = RendererMeshPhong._transform_position_to_world(light.get_light_position(), model_matrix_numpy)
                target_pos_world = RendererMeshPhong._transform_position_to_world(light.get_target_position(), model_matrix_numpy)
                light_dir = light_pos_world - target_pos_world  # surface → light source
                light_dir = light_dir / max(float(np.linalg.norm(light_dir)), 1e-12)
                light_dirs = np.broadcast_to(light_dir[np.newaxis, :], (face_count, 3))
            elif isinstance(light, PointLight):
                point_world = RendererMeshPhong._transform_position_to_world(light.get_position(), model_matrix_numpy)
                light_dirs = point_world[np.newaxis, :] - face_centroids_world  # face → light source, per face
                light_dirs = light_dirs / np.maximum(np.linalg.norm(light_dirs, axis=1, keepdims=True), 1e-12)
            else:
                # Unknown light type — skip silently
                continue

            cos_theta = np.maximum(0.0, np.sum(face_normals_world * light_dirs, axis=1))  # (face_count,)
            diffuse_term = diffuse_per_face * scaled_light[np.newaxis, :] * cos_theta[:, np.newaxis]

            # Specular (Phong): halfway vector between light_dir and view_dir.
            halfway = light_dirs + view_dirs
            halfway = halfway / np.maximum(np.linalg.norm(halfway, axis=1, keepdims=True), 1e-12)
            spec_cos = np.maximum(0.0, np.sum(face_normals_world * halfway, axis=1))
            spec_factor = np.power(spec_cos, shininess)
            specular_term = specular_per_face * scaled_light[np.newaxis, :] * spec_factor[:, np.newaxis]

            face_rgb += diffuse_term + specular_term

        return np.clip(face_rgb, 0.0, 1.0)

    @staticmethod
    def _transform_position_to_world(position_transbuf: TransBuf, model_matrix_numpy: np.ndarray) -> np.ndarray:
        """Transform a vec3 position buffer from model space to world space via the model matrix."""
        position_buffer = TransBufUtils.to_buffer(position_transbuf)
        position_numpy = Bufferx.to_numpy(position_buffer).reshape(-1, 3)  # (1, 3)
        world_xyz, _ = MathUtils.apply_transform_matrix(position_numpy, model_matrix_numpy)
        return world_xyz[0]  # (3,)
