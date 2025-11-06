# stdlib imports
import os

# local imports
from gsp.types.buffer import Buffer, BufferType
from gsp.transforms.transform_chain import TransformChain
from gsp.transforms.links.transform_data_source import TransformDataSource
from gsp.transforms.links.transform_accessor import TransformAccessor


__dirname__ = os.path.dirname(os.path.abspath(__file__))


def main():
    transformChain = TransformChain(-1, None)

    image_url = f"file://{__dirname__}/images/image.png"
    image_url = f"file://{__dirname__}/images/UV_Grid_Sm.jpg"
    transformChain.add(TransformDataSource(image_url, BufferType.uint8))
    # transformChain.add(TransformAccessor("r"))

    buffer = transformChain.run()
    print(buffer)


if __name__ == "__main__":
    main()
