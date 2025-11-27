# stdlib imports
import os

# pip imports
import numpy as np


class UuidUtils:

    GSP_UUID_COUNTER: int = 0

    @staticmethod
    def generate_uuid() -> str:
        # if GSP_UUID_COUNTER is set, use a deterministic uuid for testing purposes
        # - uuid becomes "uuid-counter-<counter>"
        if "GSP_UUID_COUNTER" in os.environ:
            _uuid = UuidUtils.GSP_UUID_COUNTER
            UuidUtils.GSP_UUID_COUNTER += 1
            return f"uuid-counter-{_uuid}"

        # uuid4 = UuidUtils._generate_uuid_v4_with_uuid()
        uuid4 = UuidUtils._generate_uuid_v4_with_numpy()
        return uuid4

    @staticmethod
    def _generate_uuid_v4_with_numpy() -> str:
        """generate a UUID version 4 using numpy for random byte generation.

        Thus it can be made deterministic by setting the numpy random seed.
        """
        # 1. Generate 16 random bytes (128 bits) using numpy
        # We use uint8 for byte representation
        random_bytes = np.random.randint(0, 256, size=16, dtype=np.uint8)

        # Convert the numpy array of bytes into a standard Python byte string
        # This is necessary because bit manipulation on numpy arrays is tricky/non-standard
        byte_string = bytes(random_bytes.tolist())

        # 2. Apply the UUID version 4 (variant 1) rules:

        # Rule 1: Set the four most significant bits of the 7th byte (octet 6) to 0100_2
        # This sets the UUID version to 4.
        # The 7th byte is at index 6 (0-indexed).
        # To set the first four bits to 0100 (4 in hex), we clear the upper 4 bits
        # and then set them to 4. (byte_string[6] & 0b1111) clears the upper bits,
        # then | 0x40 is wrong. It should be (byte_string[6] & 0x0F) | 0x40.

        # We must use a mutable structure to modify the bytes.
        # We'll use a standard Python list of integers (0-255) for easy modification.
        byte_list = list(byte_string)

        # Set Version (byte 6, index 6): 0x40 (0100xxxx)
        byte_list[6] = (byte_list[6] & 0x0F) | 0x40

        # Rule 2: Set the two most significant bits of the 9th byte (octet 8) to 10_2
        # This sets the UUID variant to 'Reserved (RFC 4122)'.
        # The 9th byte is at index 8.
        # To set the first two bits to 10 (8 in hex or 0x80), we clear the upper 2 bits
        # and then set them to 10. (byte_list[8] & 0x3F) clears the upper 2 bits,
        # then | 0x80 sets them to 10.
        byte_list[8] = (byte_list[8] & 0x3F) | 0x80

        # 3. Format the bytes into a standard UUID string format (xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx)
        # We convert the list back to bytes and then to hexadecimal.
        final_bytes = bytes(byte_list)
        hex_str = final_bytes.hex()

        # Insert hyphens
        uuid_v4 = f"{hex_str[0:8]}-{hex_str[8:12]}-{hex_str[12:16]}-{hex_str[16:20]}-{hex_str[20:32]}"

        return uuid_v4

    @staticmethod
    def _generate_uuid_v4_with_uuid() -> str:
        """Generate a UUID version 4 using the standard library uuid module."""
        import uuid

        uuid_v4 = str(uuid.uuid4())

        return uuid_v4
