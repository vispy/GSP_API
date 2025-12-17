# stdlib imports
import json
import pathlib
import sys

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
from gsp_pydantic.serializer.pydantic_parser import PydanticParser
from gsp_pydantic.types.pydantic_dict import PydanticDict
from session_record_example import PydanticSession, PydanticSessionItem


def main():
    # fix random seed for reproducibility
    np.random.seed(0)

    # =============================================================================
    # Load session file
    # =============================================================================

    gsp_session_path = pathlib.Path(__file__).parent / "output" / f"session_record_example.gsp_session.json"

    # if no file found, exit now with error
    if gsp_session_path.exists() is False:
        print(f"No existing session found at {gsp_session_path}, first create one with `./session_record_example.py`")
        sys.exit(-1)

    # read existing session in json_dict
    with open(gsp_session_path, "r") as file_reader:
        session_dict = json.load(file_reader)
    gsp_session = PydanticSession.model_validate(session_dict)

    # =============================================================================
    #
    # =============================================================================
    # create a pydantic parser
    pydantic_parser = PydanticParser()

    # get the canvas from the first item
    assert len(gsp_session.items) > 0, "No items found in the session"
    canvas, _, _, _, _ = pydantic_parser.parse(gsp_session.items[0].serialized_data)

    # =============================================================================
    # Create renderer
    # =============================================================================

    # Create a renderer
    renderer_name = ExampleHelper.get_renderer_name()
    renderer_base = ExampleHelper.create_renderer(renderer_name, canvas)

    # =============================================================================
    # Create animator
    # =============================================================================
    animator = ExampleHelper.create_animator(renderer_base)

    relative_timestamp = 0.0
    item_next_index = 0

    @animator.event_listener
    def animator_callback(delta_time: float) -> list[VisualBase]:
        nonlocal relative_timestamp, item_next_index

        # get timestamp
        relative_timestamp += delta_time

        # check if all session items have been played
        all_items_played = item_next_index >= len(gsp_session.items)
        if all_items_played:
            print("All session items have been played.")
            # return []
            sys.exit(0)

        # get the next session item
        next_item: PydanticSessionItem = gsp_session.items[item_next_index]

        # check if it's time to play the next item
        if relative_timestamp < next_item.timestamp:
            return []

        print(f"At time {relative_timestamp:.3f}s, playing session item at timestamp {next_item.timestamp:.3f}s")

        # parse the next item
        _, viewports, visuals, model_matrices, cameras = pydantic_parser.parse(next_item.serialized_data)
        renderer_base.render(viewports, visuals, model_matrices, cameras)

        # advance to the next item
        item_next_index += 1

        # return the list of changed visuals
        return []

    # =============================================================================
    # Start the animator
    # =============================================================================

    animator.start([], [], [], [])


if __name__ == "__main__":
    main()
