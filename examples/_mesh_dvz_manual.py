import pathlib

import numpy as np
import typing

import datoviz as dvz
from datoviz.visuals import Mesh as _DvzMesh


from gsp_extra.misc.mesh_utils import MeshUtils
from gsp_extra.mpl3d import glm


dvz_app = dvz.App()
figure = dvz_app.figure()
panel = figure.panel(
    background=(
        (255, 255, 255, 255),
        (255, 255, 255, 255),
        (255, 255, 255, 255),
        (255, 255, 255, 255),
    )
)
arcball = panel.arcball(initial=(0, 0, 0))


# =============================================================================
#
# =============================================================================


def create_shape_collection() -> _DvzMesh:
    """Create a shape collection with various polyhedra.

    Returns:
        _DvzMesh: A shape collection containing tetrahedron, hexahedron,
            octahedron, dodecahedron, and icosahedron with spring colormap.
    """
    N = 5
    colors = dvz.cmap("spring", np.linspace(0, 1, N))
    scale = 0.35

    shapeCollection = dvz.ShapeCollection()
    shapeCollection.add_tetrahedron(offset=(-1, 0, 0.5), scale=scale, color=colors[0])
    shapeCollection.add_hexahedron(offset=(0, 0, 0.5), scale=scale, color=colors[1])
    shapeCollection.add_octahedron(offset=(1, 0, 0.5), scale=scale, color=colors[2])
    shapeCollection.add_dodecahedron(offset=(-0.5, 0, -0.5), scale=scale, color=colors[3])
    shapeCollection.add_icosahedron(offset=(+0.5, 0, -0.5), scale=scale, color=colors[4])

    visual_multi = dvz_app.mesh(
        shapeCollection,
        lighting=True,
        contour=True,
    )
    return visual_multi


visual_multi = create_shape_collection()
panel.add(visual_multi)

# =============================================================================
# Manual triangle
# =============================================================================


def create_triangle_mesh_manual() -> _DvzMesh:
    """Create a simple triangle mesh with positions, indices, normals, and colors.

    Returns:
        _DvzMesh: A visual mesh for a single triangle.
    """
    positions = np.array(
        [
            [-0.5 + 1, 0.5, 0.0],
            [+0.5 + 1, 0.5, 0.0],
            [-0.5 + 1, -0.5, 0.0],
        ],
        dtype=np.float32,
    )

    indices = np.array([0, 2, 1], dtype=np.uint32)

    normals = np.array(
        [
            [0.0, 0.0, +1.0],
            [0.0, 0.0, +1.0],
            [0.0, 0.0, +1.0],
        ],
        dtype=np.float32,
    )

    colors = np.array(
        [
            [255, 0, 0, 255],
            [255, 0, 0, 255],
            [255, 0, 0, 255],
        ],
        dtype=np.uint8,
    )

    sc = dvz.ShapeCollection()
    sc.add_custom(
        positions=positions,
        normals=normals,
        colors=colors,
        # texcoords=texcoords,
        indices=indices,
        # offset=mesh_position,
        # scale=scale,
        # transform=model_matrix,   # TODO: Apply the model matrix transform to the mesh vertices (currently not applied
    )

    visual_mesh_manual = dvz_app.mesh(
        sc,
        lighting=True,
        contour=True,
    )

    return visual_mesh_manual


visual_mesh_manual = create_triangle_mesh_manual()
panel.add(visual_mesh_manual)

# =============================================================================
#
# =============================================================================


def createMeshFromObj(
    obj_filename: str = "head.obj",
    mesh_position: tuple[float, float, float] = (0, 0, 0),
    scale: float = 1.0,
) -> _DvzMesh:
    """Load an OBJ file and add it to the shape collection.

    Args:
        sc: The ShapeCollection to add the mesh to.
        obj_filename: Name of the OBJ file in the models directory.
        mesh_position: Position offset for the mesh.
        scale: Scale factor for the mesh.
    """
    obj_path = pathlib.Path(__file__).parent / "models" / obj_filename
    mesh_geometry = MeshUtils.parse_obj_file_manual(str(obj_path))

    positions = mesh_geometry.vertices
    indices = mesh_geometry.indices.astype(np.uint32).flatten()
    point_count = len(mesh_geometry.vertices)
    vertex_colors = np.array([[255, 0, 255, 255]] * point_count, dtype=np.uint8)
    normals = mesh_geometry.normals if mesh_geometry.normals is not None else np.zeros_like(positions, dtype=np.float32)
    texcoords = mesh_geometry.uvs if mesh_geometry.uvs is not None else np.zeros((point_count, 2), dtype=np.float32)

    position_x = 0.0
    position_y = 0.0
    position_z = 0.0
    angle_x = 0.0
    angle_y = 45.0
    angle_z = 0.0
    scale_x = 1.0
    scale_y = 1.0
    scale_z = 1.0

    matrix_rotation = glm.xrotate(angle_x) @ glm.yrotate(angle_y) @ glm.zrotate(angle_z)
    matrix_translation = glm.translate(np.array([position_x, position_y, position_z]))
    matrix_scale = glm.scale(np.array([scale_x, scale_y, scale_z]))
    matrix_mvp = matrix_translation @ matrix_scale @ matrix_rotation
    model_matrix = matrix_mvp
    transform = typing.cast(typing.Tuple[float, ...], model_matrix)

    shapeCollection = dvz.ShapeCollection()
    shapeCollection.add_custom(
        positions=positions,
        normals=normals,
        colors=vertex_colors,
        # texcoords=texcoords,
        indices=indices,
        offset=mesh_position,
        scale=scale,
        transform=transform,  # TODO: Apply the model matrix transform to the mesh vertices (currently not applied
    )

    visual_mesh = dvz_app.mesh(
        shapeCollection,
        lighting=True,
        contour=True,
    )

    visual_mesh.set_light_pos((0, 0, 1, 0))
    return visual_mesh


visual_mesh = createMeshFromObj()
panel.add(visual_mesh)

# =============================================================================
#
# =============================================================================

dvz_app.run()
dvz_app.destroy()
