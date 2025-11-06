# local imports
from gsp.types import Buffer, BufferType


def main():
    buffer = Buffer(10, BufferType.uint32)
    print("Buffer created:", buffer)

    # Set data
    buffer.set_data(bytearray(b"\x00\x00\x00\x22" * 2), 0, 2)
    print("Buffer data set.")

    # Get data
    new_buffer = buffer.get_data(0, 5)
    print("New buffer created from existing buffer:", new_buffer)
    print(f"New buffer count: {new_buffer.get_count()}")


if __name__ == "__main__":
    main()
