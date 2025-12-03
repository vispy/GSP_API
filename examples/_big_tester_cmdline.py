# stdlib imports
from typing import Literal
import typing

# pip imports
import argparse

# local imports
from common.big_tester_helper import BigTesterRunner

# =============================================================================
#
# =============================================================================


def main():
    # Parse command line arguments
    argParser = argparse.ArgumentParser(
        description="Run the big tester example.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    argParser.add_argument("--viewport-count", "--vc", type=int, default=1, help="Number of viewports to create")
    argParser.add_argument("--renderer-name", "--r", type=str, choices=["matplotlib", "datoviz", "network"], default="matplotlib", help="Renderer to use")
    argParser.add_argument(
        "--matplotlib-image-format",
        "--mif",
        type=str,
        choices=["png", "svg", "pdf"],
        default="png",
        help="Matplotlib image format. Only used if renderer is matplotlib",
    )
    argParser.add_argument("--image-path", "-o", type=str, default=None, help="Path to save image")
    argParser.add_argument(
        "--pydantic-serialize-cycle",
        "--psc",
        action="store_true",
        help="Perform a serialization cycle using Pydantic",
    )
    argParser.add_argument(
        "--scene",
        "-s",
        dest="scenes",
        type=str,
        default=["random_points"],
        nargs="+",
        choices=[
            "random_points",
            "random_pixels",
            "random_segments",
            "spiral_pixels",
        ],
        help="A required list of one or more scene.",
    )
    args = argParser.parse_args()

    # type casting for all command line args
    args.viewport_count = typing.cast(int, args.viewport_count)
    args.renderer_name = typing.cast(Literal["matplotlib", "datoviz", "network"], args.renderer_name)
    args.matplotlib_image_format = typing.cast(Literal["png", "svg", "pdf"], args.matplotlib_image_format)
    args.image_path = typing.cast(str | None, args.image_path)
    args.pydantic_serialize_cycle = typing.cast(bool, args.pydantic_serialize_cycle)
    args.scenes = typing.cast(list[Literal["random_points", "random_pixels", "random_segments", "spiral_pixels"]], args.scenes)

    BigTesterRunner.run(
        viewport_count=args.viewport_count,
        renderer_name=args.renderer_name,
        matplotlib_image_format=args.matplotlib_image_format,
        image_path=args.image_path,
        pydantic_serialize_cycle=args.pydantic_serialize_cycle,
        scenes=args.scenes,
    )


if __name__ == "__main__":
    main()
