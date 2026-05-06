# stdlib imports
import pathlib
import numpy as np
import typing

# pip imports
import datoviz as dvz
from datoviz.visuals import Mesh as _DvzMesh

# local imports
from gsp_extra.misc.mesh_utils import MeshUtils
from gsp_extra.mpl3d import glm
from gsp.types import BufferType
from gsp_extra.bufferx import Bufferx
from gsp.utils.transbuf_utils import TransBufUtils

# =============================================================================
#
# =============================================================================

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
# arcball = panel.arcball(initial=(0, 0, 0))


# =============================================================================
#
# =============================================================================


def createMeshFromObj(
    obj_filename: str = "suzanne.obj",
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

    # positions = Bufferx.to_numpy(mesh_geometry.get_vertices().
    positions_buffer = TransBufUtils.to_buffer(mesh_geometry.get_positions())
    indices_buffer = TransBufUtils.to_buffer(mesh_geometry.get_indices())
    uvs_buffer = TransBufUtils.to_buffer(mesh_geometry.get_uvs())
    normals_buffer = TransBufUtils.to_buffer(mesh_geometry.get_normals())

    positions_numpy = Bufferx.to_numpy(positions_buffer).reshape(-1, 3)
    indices_numpy = Bufferx.to_numpy(indices_buffer).flatten()
    uvs_numpy = Bufferx.to_numpy(uvs_buffer)
    normals_numpy = Bufferx.to_numpy(normals_buffer)

    position_count = positions_numpy.shape[0]
    colors_numpy = np.array([[255, 0, 255, 255]] * position_count, dtype=np.uint8)  # magenta color for all vertices

    # position_x = 0.0
    # position_y = 0.0
    # position_z = -1.0
    # angle_x = 0.0
    # angle_y = 0.0
    # angle_z = 0.0
    # scale_x = 0.5
    # scale_y = 0.5
    # scale_z = 0.5

    # model_matrix_numpy = glm.xrotate(angle_x) @ glm.yrotate(angle_y) @ glm.zrotate(angle_z)
    # axes_transform_numpy = glm.translate(np.array([position_x, position_y, position_z])) @ glm.scale(np.array([scale_x, scale_y, scale_z]))
    # model_matrix_numpy = axes_transform_numpy @ model_matrix_numpy
    # model_matrix = Bufferx.from_numpy(np.array([model_matrix_numpy]), BufferType.mat4)

    # positions_numpy = positions_numpy @ model_matrix_numpy[:3, :3].T + model_matrix_numpy[:3, 3]

    # position_x = 0.0
    # position_y = 0.0
    # position_z = 0.0
    # angle_x = 0.0
    # angle_y = 45.0
    # angle_z = 0.0
    # scale_x = 1.0
    # scale_y = 1.0
    # scale_z = 1.0

    # matrix_rotation = glm.xrotate(angle_x) @ glm.yrotate(angle_y) @ glm.zrotate(angle_z)
    # matrix_translation = glm.translate(np.array([position_x, position_y, position_z]))
    # matrix_scale = glm.scale(np.array([scale_x, scale_y, scale_z]))
    # matrix_mvp = matrix_translation @ matrix_scale @ matrix_rotation
    # model_matrix = matrix_mvp
    # transform = typing.cast(typing.Tuple[float, ...], model_matrix)

    # shapeCollection = dvz.ShapeCollection()
    # shapeCollection.add_custom(
    #     positions=vertices_numpy,
    #     normals=normals_numpy,
    #     colors=vertex_colors,
    #     # texcoords=texcoords,
    #     indices=indices_numpy,
    #     offset=mesh_position,
    #     scale=scale,
    #     transform=transform,  # TODO: Apply the model matrix transform to the mesh vertices (currently not applied
    # )

    visual_mesh = dvz_app.mesh(
        position=positions_numpy,
        normal=normals_numpy,
        color=colors_numpy,
        # texcoords=texcoords,
        index=indices_numpy,
        lighting=True,
        # contour=True,
    )
    # breakpoint()

    visual_mesh.set_light_pos((0, 0, 1, 0))
    return visual_mesh


visual_mesh = createMeshFromObj()
panel.add(visual_mesh)

# =============================================================================
#
# =============================================================================

dvz_app.run()
dvz_app.destroy()
