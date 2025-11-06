"""Tests for the Buffer class."""

import pytest
import numpy as np
from gsp.types.buffer import Buffer
from gsp.types.buffer_type import BufferType
from gsp_matplotlib.extra.bufferx import Bufferx


class TestBufferInitialization:
    """Test Buffer initialization and basic properties."""

    def test_init_with_valid_parameters(self):
        """Test creating a buffer with valid count and type."""
        buffer = Buffer(10, BufferType.float32)
        assert buffer.get_count() == 10
        assert buffer.get_type() == BufferType.float32

    def test_init_with_zero_count(self):
        """Test creating a buffer with zero count."""
        buffer = Buffer(0, BufferType.uint32)
        assert buffer.get_count() == 0
        assert buffer.get_type() == BufferType.uint32

    def test_init_with_different_buffer_types(self):
        """Test creating buffers with different buffer types."""
        types_to_test = [
            BufferType.float32,
            BufferType.uint32,
            BufferType.rgba8,
            BufferType.uint8,
            BufferType.int32,
            BufferType.int8,
            BufferType.vec2,
            BufferType.vec3,
            BufferType.vec4,
        ]

        for buffer_type in types_to_test:
            buffer = Buffer(5, buffer_type)
            assert buffer.get_count() == 5
            assert buffer.get_type() == buffer_type

    def test_repr(self):
        """Test string representation of Buffer."""
        buffer = Buffer(10, BufferType.vec3)
        expected = "Buffer(count=10, type=BufferType.vec3)"
        assert repr(buffer) == expected


class TestBufferDataOperations:
    """Test Buffer data manipulation methods."""

    def test_set_data_valid_range(self):
        """Test setting data within valid range."""
        buffer = Buffer(10, BufferType.uint8)
        test_data = bytearray([1, 2, 3, 4, 5])

        # Set data at beginning
        buffer.set_data(test_data, offset=0, count=5)

        # Set data in middle
        buffer.set_data(bytearray([10, 11]), offset=5, count=2)

    def test_set_data_at_offset(self):
        """Test setting data at various offsets."""
        buffer = Buffer(10, BufferType.uint8)

        # Test setting at offset 0
        buffer.set_data(bytearray([1, 2, 3]), offset=0, count=3)

        # Test setting at middle offset
        buffer.set_data(bytearray([4, 5]), offset=3, count=2)

        # Test setting at end
        buffer.set_data(bytearray([6]), offset=9, count=1)

    def test_set_data_invalid_range(self):
        """Test setting data beyond buffer bounds."""
        buffer = Buffer(5, BufferType.uint8)
        test_data = bytearray([1, 2, 3])

        # Should raise assertion error when offset + count > buffer size
        with pytest.raises(AssertionError):
            buffer.set_data(test_data, offset=4, count=3)

    def test_get_data_valid_range(self):
        """Test getting data within valid range."""
        buffer = Buffer(10, BufferType.uint8)
        # Fill buffer with test data
        test_data = bytearray(range(10))
        buffer.set_data(test_data, offset=0, count=10)

        # Get data from beginning
        sub_buffer = buffer.get_data(offset=0, count=3)
        assert sub_buffer.get_count() == 3
        assert sub_buffer.get_type() == BufferType.uint8

        # Get data from middle
        sub_buffer = buffer.get_data(offset=3, count=4)
        assert sub_buffer.get_count() == 4
        assert sub_buffer.get_type() == BufferType.uint8

    def test_get_data_with_larger_types(self):
        """Test getting data with larger buffer types like vec3."""
        buffer = Buffer(5, BufferType.vec3)
        # Create test data (5 vec3s = 5 * 12 bytes = 60 bytes)
        test_data = bytearray(range(60))
        buffer.set_data(test_data, offset=0, count=5)

        # Get subset
        sub_buffer = buffer.get_data(offset=1, count=2)
        assert sub_buffer.get_count() == 2
        assert sub_buffer.get_type() == BufferType.vec3


class TestBufferBytesConversion:
    """Test Buffer conversion to/from bytes."""

    def test_to_bytes(self):
        """Test converting buffer to bytes."""
        buffer = Buffer(5, BufferType.uint8)
        test_data = bytearray([1, 2, 3, 4, 5])
        buffer.set_data(test_data, offset=0, count=5)

        result = buffer.to_bytearray()
        assert isinstance(result, bytearray)
        assert len(result) == 5

    def test_from_bytes_valid_data(self):
        """Test creating buffer from valid byte data."""
        test_data = bytearray([10, 20, 30, 40])
        buffer = Buffer.from_bytearray(test_data, BufferType.uint8)

        assert buffer.get_count() == 4
        assert buffer.get_type() == BufferType.uint8

    def test_from_bytes_with_larger_types(self):
        """Test creating buffer from bytes with larger types."""
        # vec2 requires 8 bytes per element
        test_data = bytearray(range(24))  # 3 vec2s = 24 bytes
        buffer = Buffer.from_bytearray(test_data, BufferType.vec2)

        assert buffer.get_count() == 3
        assert buffer.get_type() == BufferType.vec2

    def test_from_bytes_misaligned_data(self):
        """Test creating buffer from misaligned byte data."""
        # vec3 requires 12 bytes per element, so 10 bytes should fail
        test_data = bytearray(range(10))

        with pytest.raises(AssertionError):
            Buffer.from_bytearray(test_data, BufferType.vec3)

    def test_bytes_roundtrip(self):
        """Test roundtrip conversion: Buffer -> bytes -> Buffer."""
        original = Buffer(3, BufferType.uint32)
        test_data = bytearray(range(12))  # 3 uint32s = 12 bytes
        original.set_data(test_data, offset=0, count=3)

        # Convert to bytes and back
        bytes_data = original.to_bytearray()
        reconstructed = Buffer.from_bytearray(bytes_data, BufferType.uint32)

        assert reconstructed.get_count() == original.get_count()
        assert reconstructed.get_type() == original.get_type()


class TestBufferNumpyConversion:
    """Test Buffer conversion to/from numpy arrays."""

    def test_to_numpy_scalar_types(self):
        """Test converting scalar buffer types to numpy."""
        scalar_types = [
            (BufferType.float32, np.float32),
            (BufferType.uint32, np.uint32),
            (BufferType.uint8, np.uint8),
            (BufferType.int32, np.int32),
            (BufferType.int8, np.int8),
        ]

        for buffer_type, expected_dtype in scalar_types:
            buffer = Buffer(5, buffer_type)
            numpy_array = Bufferx.to_numpy(buffer)

            assert numpy_array.dtype == expected_dtype
            assert numpy_array.shape == (5, 1)

    def test_to_numpy_vector_types(self):
        """Test converting vector buffer types to numpy."""
        vector_types = [
            (BufferType.vec2, (5, 2)),
            (BufferType.vec3, (5, 3)),
            (BufferType.vec4, (5, 4)),
        ]

        for buffer_type, expected_shape in vector_types:
            buffer = Buffer(5, buffer_type)
            numpy_array = Bufferx.to_numpy(buffer)

            assert numpy_array.dtype == np.float32
            assert numpy_array.shape == expected_shape

    def test_to_numpy_with_data(self):
        """Test numpy conversion with actual data."""
        buffer = Buffer(3, BufferType.uint8)
        test_data = bytearray([10, 20, 30])
        buffer.set_data(test_data, offset=0, count=3)

        numpy_array = Bufferx.to_numpy(buffer)
        expected = np.array([[10], [20], [30]], dtype=np.uint8)

        np.testing.assert_array_equal(numpy_array, expected)

    def test_to_numpy_vec3_with_data(self):
        """Test numpy conversion for vec3 with actual data."""
        buffer = Buffer(2, BufferType.vec3)
        # Create test data for 2 vec3s (2 * 12 bytes = 24 bytes)
        # Using float32 values: [1.0, 2.0, 3.0] and [4.0, 5.0, 6.0]
        test_data = bytearray()
        for val in [1.0, 2.0, 3.0, 4.0, 5.0, 6.0]:
            test_data.extend(np.array([val], dtype=np.float32).tobytes())

        buffer.set_data(test_data, offset=0, count=2)

        numpy_array = Bufferx.to_numpy(buffer)

        expected = np.array([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]], dtype=np.float32)
        np.testing.assert_array_almost_equal(numpy_array, expected)


class TestBufferEdgeCases:
    """Test Buffer edge cases and error conditions."""

    def test_empty_buffer_operations(self):
        """Test operations on empty buffer."""
        buffer = Buffer(0, BufferType.float32)

        # Should be able to get bytes from empty buffer
        bytes_data = buffer.to_bytearray()
        assert len(bytes_data) == 0

        # Should be able to convert to numpy
        numpy_array = Bufferx.to_numpy(buffer)
        assert numpy_array.shape == (0, 1)

    def test_large_buffer_creation(self):
        """Test creating a large buffer."""
        large_count = 10000
        buffer = Buffer(large_count, BufferType.float32)

        assert buffer.get_count() == large_count
        assert buffer.get_type() == BufferType.float32

    def test_buffer_type_consistency(self):
        """Test that buffer maintains type consistency throughout operations."""
        for buffer_type in BufferType:
            buffer = Buffer(5, buffer_type)

            # Type should remain consistent after operations
            assert buffer.get_type() == buffer_type

            # Get data should preserve type
            if buffer.get_count() > 0:
                sub_buffer = buffer.get_data(0, min(2, buffer.get_count()))
                assert sub_buffer.get_type() == buffer_type


class TestBufferWithDifferentSizes:
    """Test Buffer behavior with different element sizes."""

    def test_item_size_calculation(self):
        """Test that buffers handle different item sizes correctly."""
        # Test data: (buffer_type, count, expected_total_bytes)
        test_cases = [
            (BufferType.uint8, 10, 10),  # 1 byte per element
            (BufferType.float32, 10, 40),  # 4 bytes per element
            (BufferType.vec2, 5, 40),  # 8 bytes per element
            (BufferType.vec3, 3, 36),  # 12 bytes per element
            (BufferType.vec4, 2, 32),  # 16 bytes per element
        ]

        for buffer_type, count, expected_bytes in test_cases:
            buffer = Buffer(count, buffer_type)
            bytes_data = buffer.to_bytearray()
            assert len(bytes_data) == expected_bytes

    def test_partial_data_operations(self):
        """Test operations that work with partial buffer data."""
        buffer = Buffer(10, BufferType.uint32)

        # Set partial data
        partial_data = bytearray(range(20))  # 5 uint32s worth of data
        buffer.set_data(partial_data, offset=2, count=5)

        # Get partial data
        sub_buffer = buffer.get_data(offset=3, count=3)
        assert sub_buffer.get_count() == 3
        assert sub_buffer.get_type() == BufferType.uint32
