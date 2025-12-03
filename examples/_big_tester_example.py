# stdlib imports
import pathlib
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
    output_path: pathlib.Path = pathlib.Path(__file__).parent / "output"

    # default image path
    BigTesterRunner.run(
        viewport_count=4,
        renderer_name="matplotlib",
        matplotlib_image_format="png",
        image_path=str(output_path / f"{pathlib.Path(__file__).stem}_matplotlib.png"),
        pydantic_serialize_cycle=True,
        scenes=["random_points"],
    )


if __name__ == "__main__":
    main()
