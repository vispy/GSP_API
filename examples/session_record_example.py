# stdlib imports
import json
import pathlib

# pip imports
import numpy as np
from pydantic import BaseModel


# local imports
from gsp.constants import Constants
from gsp.core import Canvas, Viewport
from gsp.visuals import Points
from gsp.types import Buffer, BufferType
from gsp.core import Camera
from gsp_extra.bufferx import Bufferx
from gsp.utils.unit_utils import UnitUtils
from common.example_helper import ExampleHelper
from gsp_extra.camera_controls.object_controls_trackball import ObjectControlsTrackball
from gsp.types.visual_base import VisualBase
from gsp_pydantic.serializer.pydantic_serializer import PydanticSerializer
from gsp_pydantic.types.pydantic_dict import PydanticDict


# =============================================================================
# Pydantic models
# =============================================================================
class PydanticSessionItem(BaseModel):
    timestamp: float
    serialized_data: PydanticDict


class PydanticSession(BaseModel):
    items: list[PydanticSessionItem]


# =============================================================================
# main()
# =============================================================================
def main():
    # fix random seed for reproducibility
    np.random.seed(0)

    # Create a canvas
    canvas = Canvas(256, 256, 72.0)

    # Create a viewport and add it to the canvas
    viewport = Viewport(0, 0, canvas.get_width(), canvas.get_height())

    # =============================================================================
    # Add random points
    # - various ways to create Buffers
    # =============================================================================
    point_count = 100

    # Random positions - Create buffer from numpy array
    positions_numpy = np.random.rand(point_count, 3).astype(np.float32) * 2.0 - 1
    positions_buffer = Bufferx.from_numpy(positions_numpy, BufferType.vec3)

    # Sizes - Create buffer and set data with numpy array
    sizes_numpy = np.array([40] * point_count, dtype=np.float32)
    sizes_buffer = Bufferx.from_numpy(sizes_numpy, BufferType.float32)

    # all pixels red - Create buffer and fill it with a constant
    face_colors_buffer = Buffer(point_count, BufferType.rgba8)
    face_colors_buffer.set_data(Constants.Color.red * point_count, 0, point_count)

    # Edge colors - Create buffer and fill it with a constant
    edge_colors_buffer = Buffer(point_count, BufferType.rgba8)
    edge_colors_buffer.set_data(Constants.Color.blue * point_count, 0, point_count)

    # Edge widths - Create buffer and fill it with a constant
    edge_widths_numpy = np.array([UnitUtils.pixel_to_point(1, canvas.get_dpi())] * point_count, dtype=np.float32)
    edge_widths_buffer = Bufferx.from_numpy(edge_widths_numpy, BufferType.float32)

    # Create the Points visual and add it to the viewport
    points = Points(positions_buffer, sizes_buffer, face_colors_buffer, edge_colors_buffer, edge_widths_buffer)

    # =============================================================================
    # Render the canvas
    # =============================================================================

    model_matrix = Bufferx.mat4_identity()
    # Create a camera
    camera = Camera(Bufferx.mat4_identity(), Bufferx.mat4_identity())

    # =============================================================================
    # Render
    # =============================================================================

    # Create a renderer
    renderer_name = ExampleHelper.get_renderer_name()
    renderer_base = ExampleHelper.create_renderer(renderer_name, canvas)

    # =============================================================================
    # Create Viewport events
    # =============================================================================

    viewport_events = ExampleHelper.create_viewport_events(renderer_base, viewport)
    object_controls = ObjectControlsTrackball(model_matrix, viewport_events)

    # =============================================================================
    # Create animator
    # =============================================================================
    animator = ExampleHelper.create_animator(renderer_base)

    # =============================================================================
    # Record the GSP session
    # =============================================================================

    gsp_session: PydanticSession = PydanticSession(items=[])
    pydantic_serializer = PydanticSerializer(canvas)

    relative_timestamp = 0.0

    @animator.event_listener
    def animator_callback(delta_time: float) -> list[VisualBase]:
        # get timestamp
        nonlocal relative_timestamp
        relative_timestamp += delta_time

        # Serialize the scene
        serialized_data: PydanticDict = pydantic_serializer.serialize(
            viewports=[viewport],
            visuals=[points],
            model_matrices=[model_matrix],
            cameras=[camera],
        )

        # Check the scene differs from last saved frame, if no changes, do nothing
        if len(gsp_session.items) > 0 and serialized_data == gsp_session.items[-1].serialized_data:
            return []

        # print(f"Session recording at time {relative_timestamp}, delta_time: {delta_time}")

        # create a new session item
        sessionItem: PydanticSessionItem = PydanticSessionItem(
            timestamp=relative_timestamp,
            serialized_data=serialized_data,
        )

        # add the session item to the session
        gsp_session.items.append(sessionItem)

        # return the list of changed visuals
        return []

    # =============================================================================
    # Start the animator
    # =============================================================================

    animator.start([viewport], [points], [model_matrix], [camera])

    # =============================================================================
    # Save the gsp_session
    # =============================================================================

    # sanity check
    assert len(gsp_session.items) > 0, "No items found in the session"

    # Save the session to a JSON file
    gsp_session_dict = gsp_session.model_dump()
    gsp_session_path = pathlib.Path(__file__).parent / "output" / f"{pathlib.Path(__file__).stem}.gsp_session.json"
    with open(gsp_session_path, "w") as file_writer:
        json.dump(gsp_session_dict, file_writer, indent=4)

    # log the event
    print(f"Session saved to {gsp_session_path}")


if __name__ == "__main__":
    main()
