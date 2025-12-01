# stdlib imports
import os
import pathlib
import json

# pip imports
import numpy as np

# local imports
from gsp.core import Canvas, Viewport
from gsp.visuals import Pixels
from gsp.types import Buffer, BufferType
from gsp.core import Camera
from gsp_extra.bufferx import Bufferx
from gsp.utils.group_utils import GroupUtils
from gsp_pydantic.serializer.pydantic_parser import PydanticParser
from gsp_pydantic.serializer.pydantic_serializer import PydanticSerializer
from gsp_pydantic.types.pydantic_dict import PydanticDict
from gsp.transforms.transform_chain import TransformChain
from gsp.transforms.links.transform_link_immediate import TransformLinkImmediate
from common.example_helper import ExampleHelper


def main():
    # fix random seed for reproducibility
    np.random.seed(0)

    # Create a canvas
    canvas = Canvas(100, 100, 96.0)

    # Create a viewport and add it to the canvas
    viewport = Viewport(0, 0, canvas.get_width(), canvas.get_height())

    # =============================================================================
    # Add random points
    # - various ways to create Buffers
    # =============================================================================

    point_count = 10_000
    group_size = point_count
    group_count = GroupUtils.get_group_count(point_count, groups=group_size)

    # Random positions - Create buffer from numpy array
    positions_numpy = np.random.rand(point_count, 3).astype(np.float32) * 2.0 - 1
    positions_buffer = Bufferx.from_numpy(positions_numpy, BufferType.vec3)

    # all pixels red - Create buffer and fill it with a constant
    colors_buffer = Buffer(group_count, BufferType.rgba8)
    colors_buffer.set_data(bytearray([255, 0, 0, 255]) * group_count, 0, group_count)
    colors_transform = TransformChain(buffer_count=group_count, buffer_type=BufferType.rgba8)
    colors_transform.add(TransformLinkImmediate(colors_buffer))

    # Create the Pixels visual and add it to the viewport
    pixels = Pixels(positions_buffer, colors_transform, groups=group_size)

    # =============================================================================
    # Render the canvas
    # =============================================================================

    model_matrix = Bufferx.mat4_identity()
    # Create a camera
    camera = Camera(Bufferx.mat4_identity(), Bufferx.mat4_identity())

    # =============================================================================
    # Serialize with Pydantic
    # =============================================================================

    # Serialize the scene
    pydantic_serializer = PydanticSerializer(canvas)
    serialized_data: PydanticDict = pydantic_serializer.serialize(
        viewports=[viewport],
        visuals=[pixels],
        model_matrices=[model_matrix],
        cameras=[camera],
    )

    # convert to JSON string
    serialized_json_str: str = json.dumps(serialized_data, indent=4)

    # Print serialized data
    print(serialized_data)

    # Save to file
    output_basename = f"{pathlib.Path(__file__).stem}.gsp_pydantic.json"
    output_path = pathlib.Path(__file__).parent / "output" / output_basename
    with open(output_path, "w") as file_writer:
        file_writer.write(serialized_json_str)

    # =============================================================================
    # Deserialize with pydantic
    # =============================================================================

    parsed_canvas, parsed_viewports, parsed_visuals, parsed_model_matrices, parsed_cameras = PydanticParser().parse(serialized_data)

    # =============================================================================
    # Render
    # =============================================================================

    # Create renderer and render
    renderer_name = ExampleHelper.get_renderer_name()
    renderer_base = ExampleHelper.create_renderer(renderer_name, parsed_canvas)
    rendered_image = renderer_base.render(parsed_viewports, parsed_visuals, parsed_model_matrices, parsed_cameras)

    # Save to file
    ExampleHelper.save_output_image(rendered_image, f"{pathlib.Path(__file__).stem}_{renderer_name}.png")

    # Show the renderer
    renderer_base.show()


if __name__ == "__main__":
    main()
