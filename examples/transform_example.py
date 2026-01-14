"""Example of using TransformChain to load an image into a Buffer."""

# stdlib imports
import os

# local imports
from gsp.types.buffer import Buffer, BufferType
from gsp.transforms.transform_chain import TransformChain
from gsp_extra.transform_links.transform_load import TransformLoad


__dirname__ = os.path.dirname(os.path.abspath(__file__))


def main():
    """Main function for the transform example."""
    transformChain = TransformChain(-1, None)

    image_url = f"file://{__dirname__}/images/image.png"
    image_url = f"file://{__dirname__}/images/UV_Grid_Sm.jpg"
    transformChain.add(TransformLoad(image_url, BufferType.uint8))

    buffer = transformChain.run()
    print(buffer)


if __name__ == "__main__":
    main()
