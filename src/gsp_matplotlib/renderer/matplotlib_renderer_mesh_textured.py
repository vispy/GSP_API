"""Matplotlib renderer for MeshTexturedMaterial — per-face AxesImage with affine warp."""

# stdlib imports
import typing

# pip imports
import matplotlib.artist
import matplotlib.axes
import matplotlib.image
import matplotlib.path
import matplotlib.transforms
import numpy as np

# local imports
from gsp.core.viewport import Viewport
from gsp.materials.mesh_textured_material import MeshTexturedMaterial
from gsp.utils.transbuf_utils import TransBufUtils
from gsp.visuals.mesh import Mesh
from .matplotlib_renderer import MatplotlibRenderer
from .matplotlib_renderer_mesh_phong import RendererMeshPhong
from ..extra.bufferx import Bufferx
from ..utils.renderer_utils import RendererUtils


class RendererMeshTextured:
    """Render a Mesh with MeshTexturedMaterial: one matplotlib AxesImage per triangle."""

    @staticmethod
    def render(
        renderer: MatplotlibRenderer,
        viewport: Viewport,
        mesh: Mesh,
        geometry_indices_numpy: np.ndarray,
        vertices_world_numpy: np.ndarray,
        faces_vertices_ndc: np.ndarray,
        faces_vertices_2d: np.ndarray,
        model_matrix_numpy: np.ndarray,
        camera_position_world: np.ndarray,
        vertex_count: int,
        face_count: int,
    ) -> list[matplotlib.artist.Artist]:
        """Render the mesh by creating one AxesImage per triangle and warping the texture.

        Args:
            renderer (MatplotlibRenderer): The matplotlib renderer instance.
            viewport (Viewport): Viewport to render onto.
            mesh (Mesh): Mesh with MeshTexturedMaterial.
            geometry_indices_numpy (np.ndarray): (face_count, 3) triangle indices.
            vertices_world_numpy (np.ndarray): (vertex_count, 3) world-space vertices.
            faces_vertices_ndc (np.ndarray): (face_count, 3, 3) per-face NDC vertices, used for depth sorting.
            faces_vertices_2d (np.ndarray): (face_count, 3, 2) per-face screen-space vertices.
            model_matrix_numpy (np.ndarray): (4, 4) model matrix.
            camera_position_world (np.ndarray): (3,) camera position in world space.
            vertex_count (int): Number of vertices.
            face_count (int): Number of faces.

        Returns:
            list[matplotlib.artist.Artist]: AxesImage artists (one per face).
        """
        material = mesh.get_material()
        assert isinstance(material, MeshTexturedMaterial), f"Expected MeshTexturedMaterial, got {type(material)}"

        mpl_axes = renderer.get_mpl_axes_for_viewport(viewport)

        # =============================================================================
        # Per-face UVs
        # =============================================================================

        uvs_buffer = TransBufUtils.to_buffer(mesh.get_geometry().get_uvs())
        uvs_numpy = Bufferx.to_numpy(uvs_buffer).reshape(-1, 2)  # (vertex_count, 2)
        faces_uvs = uvs_numpy[geometry_indices_numpy]  # (face_count, 3, 2)

        # =============================================================================
        # Texture data as (H, W, 4) float in [0, 1]
        # =============================================================================

        texture = material.get_texture()
        texture_data_buffer = TransBufUtils.to_buffer(texture.get_data())
        texture_pixels = Bufferx.to_numpy(texture_data_buffer)  # (W*H, 4) uint8
        texture_width = texture.get_width()
        texture_height = texture.get_height()
        texture_hwc = texture_pixels.reshape(texture_height, texture_width, 4).astype(np.float32) / 255.0

        # =============================================================================
        # Face culling
        # =============================================================================

        faces_visible = RendererUtils.compute_faces_visible(faces_vertices_2d, material.get_face_culling())

        # =============================================================================
        # Phong shading → per-face tint
        # =============================================================================

        face_normals_world = RendererUtils.compute_face_normals_world(vertices_world_numpy, geometry_indices_numpy)
        faces_vertices_world = vertices_world_numpy[geometry_indices_numpy]  # (face_count, 3, 3)
        face_centroids_world = faces_vertices_world.mean(axis=1)

        color_buffer = TransBufUtils.to_buffer(material.get_color())
        specular_buffer = TransBufUtils.to_buffer(material.get_specular_color())
        color_numpy = Bufferx.to_numpy(color_buffer)[:, :3] / 255.0  # (N, 3)
        specular_numpy = Bufferx.to_numpy(specular_buffer)[:, :3] / 255.0
        color_per_face = RendererUtils.to_per_face(color_numpy, face_count, vertex_count, geometry_indices_numpy)
        specular_per_face = RendererUtils.to_per_face(specular_numpy, face_count, vertex_count, geometry_indices_numpy)

        face_shade_rgb = RendererMeshPhong.shade_faces_flat(
            diffuse_per_face=color_per_face,
            specular_per_face=specular_per_face,
            shininess=material.get_shininess(),
            lights=material.get_lights(),
            face_normals_world=face_normals_world,
            face_centroids_world=face_centroids_world,
            camera_position_world=camera_position_world,
            model_matrix_numpy=model_matrix_numpy,
            face_count=face_count,
        )  # (face_count, 3) in [0, 1]

        # =============================================================================
        # Per-face depth for zorder — NDC z (camera-aware), same metric as the other materials.
        #
        # NDC z runs from -1 (near plane, closest to camera) to +1 (far plane). Painter's
        # algorithm wants the near faces drawn ON TOP, which in matplotlib means higher
        # zorder for nearer faces — hence the negation when calling set_zorder() below.
        # The matplotlib_scenegraph reference uses mean world Z here, which is wrong as soon
        # as the camera isn't sitting at the origin looking down +Z.
        # =============================================================================

        faces_depth_ndc = RendererUtils.compute_face_depths_ndc(faces_vertices_ndc)

        # =============================================================================
        # Lazily create one AxesImage per face
        # =============================================================================

        fake_texture = np.zeros((1, 1, 3), dtype=np.uint8)
        for face_index in range(face_count):
            face_uuid = f"{mesh.get_uuid()}_face_{face_index}"
            if face_uuid not in renderer._artists:
                axes_image = mpl_axes.imshow(fake_texture, origin="lower", extent=(0, 0, 0, 0))
                axes_image.set_visible(False)
                renderer._artists[face_uuid] = axes_image

        # =============================================================================
        # Per-face update
        # =============================================================================

        changed_artists: list[matplotlib.artist.Artist] = []
        face_sorting = material.get_face_sorting()
        for face_index in range(face_count):
            face_uuid = f"{mesh.get_uuid()}_face_{face_index}"
            axes_image = typing.cast(matplotlib.image.AxesImage, renderer._artists[face_uuid])
            changed_artists.append(axes_image)

            face_visible = bool(faces_visible[face_index])
            axes_image.set_visible(face_visible)

            if face_sorting:
                # NDC z near plane is -1 (closest), far plane is +1. Higher zorder draws on top,
                # so flip the sign: nearer faces get larger zorder.
                axes_image.set_zorder(-float(faces_depth_ndc[face_index]))

            if not face_visible:
                continue

            RendererMeshTextured._update_textured_face(
                mpl_axes=mpl_axes,
                axes_image=axes_image,
                face_vertices_2d=faces_vertices_2d[face_index],
                face_uvs=faces_uvs[face_index],
                texture_hwc=texture_hwc,
                face_color_rgb=face_shade_rgb[face_index],
            )

        return changed_artists

    # =============================================================================
    # Per-face artist update — port of matplotlib_scenegraph update_textured_face
    # =============================================================================

    @staticmethod
    def _update_textured_face(
        mpl_axes: matplotlib.axes.Axes,
        axes_image: matplotlib.image.AxesImage,
        face_vertices_2d: np.ndarray,
        face_uvs: np.ndarray,
        texture_hwc: np.ndarray,
        face_color_rgb: np.ndarray,
        interpolation: str = "none",
    ) -> None:
        """Position and texture one AxesImage to match a single triangle."""
        assert face_vertices_2d.shape == (3, 2), f"face_vertices_2d shape should be (3, 2), got {face_vertices_2d.shape}"
        assert face_uvs.shape == (3, 2), f"face_uvs shape should be (3, 2), got {face_uvs.shape}"
        assert face_color_rgb.shape == (3,), f"face_color_rgb shape should be (3,), got {face_color_rgb.shape}"

        image_h, image_w = texture_hwc.shape[:2]
        uvs_pixel = face_uvs * (image_w, image_h)

        x_min = int(np.floor(uvs_pixel[:, 0].min()))
        x_max = int(np.ceil(uvs_pixel[:, 0].max()))
        y_min = int(np.floor(uvs_pixel[:, 1].min()))
        y_max = int(np.ceil(uvs_pixel[:, 1].max()))

        x_min = max(0, min(x_min, image_w))
        x_max = max(0, min(x_max, image_w))
        y_min = max(0, min(y_min, image_h))
        y_max = max(0, min(y_max, image_h))

        if x_max <= x_min or y_max <= y_min:
            axes_image.set_extent((0, 0, 0, 0))
            return

        texture_region = texture_hwc[y_min:y_max, x_min:x_max, :3] * face_color_rgb  # tint
        texture_region = np.clip(texture_region * 255.0, 0, 255).astype(np.uint8)
        extent = (x_min / image_w, x_max / image_w, y_min / image_h, y_max / image_h)

        matrix_wrap = RendererMeshTextured._texture_coords_wrap(face_uvs, face_vertices_2d)
        if matrix_wrap is None:
            axes_image.set_extent((0, 0, 0, 0))
            return

        transform = matrix_wrap + mpl_axes.transData

        path = matplotlib.path.Path(
            [face_uvs[0], face_uvs[1], face_uvs[2], face_uvs[0]],
            closed=True,
        )

        axes_image.set_data(texture_region)
        axes_image.set_interpolation(interpolation)
        axes_image.set_extent(extent)
        axes_image.set_transform(transform)
        axes_image.set_clip_path(path, transform)

    # =============================================================================
    # Affine mapping from UV-space triangle to screen-space triangle
    # =============================================================================

    @staticmethod
    def _texture_coords_wrap(
        face_coord_uv: np.ndarray,
        face_coord_screen: np.ndarray,
    ) -> matplotlib.transforms.Affine2D | None:
        """Affine transform that warps the UV triangle into the screen-space triangle.

        Returns None for degenerate triangles (singular UV matrix).
        """
        homogeneous_uv = np.c_[np.array(face_coord_uv), np.ones(3)]
        homogeneous_screen = np.c_[np.array(face_coord_screen), np.ones(3)]
        try:
            matrix = np.linalg.inv(homogeneous_uv) @ homogeneous_screen
        except np.linalg.LinAlgError:
            return None
        return matplotlib.transforms.Affine2D(matrix.T)
