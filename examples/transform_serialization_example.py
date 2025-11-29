# stdlib imports
import os

# pip imports
import json

# local imports
from gsp.types.buffer import Buffer, BufferType
from gsp.transforms.transform_chain import TransformChain
from gsp.transforms.links.transform_data_source import TransformDataSource
from gsp_extra.transform_links import TransformLinkImmediate


__dirname__ = os.path.dirname(os.path.abspath(__file__))


def main():

    # =============================================================================
    # Create a transform chain
    # =============================================================================

    transformChain = TransformChain(-1, None)

    resulting_buffer = Buffer(4, BufferType.uint8)
    resulting_buffer.set_data(bytearray([1, 2, 3, 4]), 0, 4)
    transform_link_immediate = TransformLinkImmediate(resulting_buffer)
    transformChain.add(transform_link_immediate)

    image_url = f"file://{__dirname__}/images/UV_Grid_Sm.jpg"
    transformChain.add(TransformDataSource(image_url, BufferType.uint8))

    # =============================================================================
    # Serialize/deserialize the transformChain
    # =============================================================================

    # Serialize the transform chain
    transform_serialized = transformChain.serialize()

    # Display the serialized transformChain
    print("Serialized TransformChain (JSON):", json.dumps(transform_serialized, indent=4))

    # Deserialize the transform chain
    transform_deserialized = TransformChain.deserialize(transform_serialized)

    # =============================================================================
    # Run the transform chains and compare results
    # =============================================================================

    # Evaluate both chains and compare results
    resulting_buffer_original = transformChain.run()
    resulting_buffer_deserialized = transform_deserialized.run()

    # Compare the resulting buffers
    resulting_bytearray_original = resulting_buffer_original.to_bytearray()
    resulting_bytearray_deserialized = resulting_buffer_deserialized.to_bytearray()
    if resulting_bytearray_original == resulting_bytearray_deserialized:
        print("✅ Success: The original and deserialized transform chains produce the same buffer data.")
    else:
        print("❌ Error: The original and deserialized transform chains produce different buffer data.")

    # # Display the resulting buffer data in hex format
    # print("Buffer Data Original (Hex):", [hex(byte_value) for byte_value in resulting_buffer_original.to_bytearray()])
    # print("Buffer Data Deserialized (Hex):", [hex(byte_value) for byte_value in resulting_buffer_deserialized.to_bytearray()])

    # sanity check
    assert resulting_bytearray_original == resulting_bytearray_deserialized, "Buffer data mismatch after serialization/deserialization."


if __name__ == "__main__":

    main()
