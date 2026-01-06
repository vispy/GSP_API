"""Example showing how to use the Animator to create an animation with random point sizes."""

# stdlib imports
import os
import pathlib
import argparse

# pip imports
import numpy as np

# local imports
from common.example_helper import ExampleHelper
from gsp.constants import Constants
from gsp.core import Canvas, Viewport
from gsp.types.visual_base import VisualBase
from gsp.visuals import Points
from gsp.types import Buffer, BufferType
from gsp.core import Camera
from gsp.utils.unit_utils import UnitUtils
from gsp_extra.bufferx import Bufferx

__dirname__ = pathlib.Path(__file__).parent.resolve()


def main(save_video: bool):
    """Main function for the points animator example."""
    # fix random seed for reproducibility
    np.random.seed(0)

    # Create a canvas
    canvas = Canvas(100, 100, 72.0)

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
    face_colors_buffer.set_data(bytearray([255, 0, 0, 255]) * point_count, 0, point_count)

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
    # Create the renderer
    # =============================================================================

    renderer_name = ExampleHelper.get_renderer_name()
    renderer_base = ExampleHelper.create_renderer(renderer_name, canvas)

    # =============================================================================
    # Create the animator with/without save_video
    # =============================================================================

    if save_video is False:
        # init the animator with the renderer
        animator = ExampleHelper.create_animator(renderer_base)
    else:
        # Save the animation to a video file
        video_path = os.path.join(__dirname__, f"output/{os.path.basename(__file__).replace('.py', '')}_{renderer_name}.mp4")
        print(f"Saving video to {video_path}")

        # init the animator with the renderer
        animator = ExampleHelper.create_animator_with_video(renderer_base, video_path, fps=60, video_duration=10.0)

        # event notified when the video is saved/completed, to stop the animator and close the renderer
        @animator.on_video_saved.event_listener
        def on_save():
            # log the video path
            print(f"Video saved to: {video_path}")

            # stop the animator
            animator.stop()

            # close the renderer
            renderer_base.close()

    # =============================================================================
    # Start the animator
    # =============================================================================

    @animator.event_listener
    def animator_callback(delta_time: float) -> list[VisualBase]:
        sizes_numpy = np.random.rand(point_count).astype(np.float32) * 40.0 + 10.0
        sizes_buffer.set_data(bytearray(sizes_numpy.tobytes()), 0, sizes_buffer.get_count())

        changed_visuals: list[VisualBase] = [points]
        return changed_visuals

    # start the animation loop
    animator.start([viewport], [points], [model_matrix], [camera])


# =============================================================================
# Main entry point
# =============================================================================
if __name__ == "__main__":
    # Parse command line arguments
    argParser = argparse.ArgumentParser(
        description="Run the animator matplotlib example.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    argParser.add_argument(
        "--save-video",
        "--sv",
        action="store_true",
        help="Save the animation to a video file.",
    )
    args = argParser.parse_args()
    # args = argParser.parse_args(["--save-video"])  # for testing purpose, replace with args = argParser.parse_args()

    main(save_video=args.save_video)
