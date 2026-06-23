"""Tests for S022 no-network `.npy` decoder policy validation."""

from __future__ import annotations

from io import BytesIO

import numpy as np

from gsp.protocol import S022NpyDecoderPolicy, SecurityDiagnosticCode, validate_s022_npy_decoder_payload


def _npy_bytes(array: np.ndarray) -> bytes:
    buffer = BytesIO()
    np.save(buffer, array, allow_pickle=True)
    return buffer.getvalue()


def _policy(**overrides: object) -> S022NpyDecoderPolicy:
    values: dict[str, object] = {
        "expected_shape": (2, 2),
        "expected_dtype": "float32",
    }
    values.update(overrides)
    return S022NpyDecoderPolicy(**values)  # type: ignore[arg-type]


def test_s022_npy_decoder_accepts_bounded_float32_payload():
    payload = _npy_bytes(np.arange(4, dtype=np.float32).reshape(2, 2))

    result = validate_s022_npy_decoder_payload(payload, _policy())

    assert result.accepted
    assert result.header is not None
    assert result.header.shape == (2, 2)
    assert result.header.dtype == "float32"
    assert result.header.decoded_bytes == 16


def test_s022_npy_decoder_rejects_invalid_magic_and_version():
    invalid_magic = validate_s022_npy_decoder_payload(b"not-npy", _policy())
    invalid_version_payload = bytearray(_npy_bytes(np.zeros((2, 2), dtype=np.float32)))
    invalid_version_payload[6] = 9
    invalid_version = validate_s022_npy_decoder_payload(bytes(invalid_version_payload), _policy())

    assert not invalid_magic.accepted
    assert not invalid_version.accepted
    assert SecurityDiagnosticCode.CHUNK_METADATA_INVALID in invalid_magic.codes
    assert SecurityDiagnosticCode.CHUNK_METADATA_INVALID in invalid_version.codes


def test_s022_npy_decoder_rejects_object_dtype_pickle_payload():
    payload = _npy_bytes(np.array([{"forbidden": "object"}], dtype=object))

    result = validate_s022_npy_decoder_payload(payload, _policy(expected_shape=(1,), expected_dtype="object"))

    assert not result.accepted
    assert SecurityDiagnosticCode.CHUNK_METADATA_INVALID in result.codes


def test_s022_npy_decoder_rejects_structured_and_string_dtypes():
    structured = _npy_bytes(np.array([(1, 2)], dtype=[("x", "<i4"), ("y", "<i4")]))
    string = _npy_bytes(np.array(["bad"], dtype="<U3"))

    structured_result = validate_s022_npy_decoder_payload(structured, _policy(expected_shape=(1,), expected_dtype="void64"))
    string_result = validate_s022_npy_decoder_payload(string, _policy(expected_shape=(1,), expected_dtype="str96"))

    assert not structured_result.accepted
    assert not string_result.accepted
    assert SecurityDiagnosticCode.CHUNK_METADATA_INVALID in structured_result.codes
    assert SecurityDiagnosticCode.CHUNK_METADATA_INVALID in string_result.codes


def test_s022_npy_decoder_rejects_fortran_order_and_big_endian_dtype():
    fortran = _npy_bytes(np.asfortranarray(np.zeros((2, 2), dtype=np.float32)))
    big_endian = _npy_bytes(np.zeros((2, 2), dtype=">f4"))

    fortran_result = validate_s022_npy_decoder_payload(fortran, _policy())
    big_endian_result = validate_s022_npy_decoder_payload(big_endian, _policy())

    assert not fortran_result.accepted
    assert not big_endian_result.accepted
    assert SecurityDiagnosticCode.CHUNK_METADATA_INVALID in fortran_result.codes
    assert SecurityDiagnosticCode.CHUNK_METADATA_INVALID in big_endian_result.codes


def test_s022_npy_decoder_rejects_shape_dtype_and_trailing_byte_mismatch():
    shape_mismatch = _npy_bytes(np.zeros((2, 3), dtype=np.float32))
    dtype_mismatch = _npy_bytes(np.zeros((2, 2), dtype=np.uint8))
    trailing = _npy_bytes(np.zeros((2, 2), dtype=np.float32)) + b"x"

    shape_result = validate_s022_npy_decoder_payload(shape_mismatch, _policy())
    dtype_result = validate_s022_npy_decoder_payload(dtype_mismatch, _policy())
    trailing_result = validate_s022_npy_decoder_payload(trailing, _policy())

    assert not shape_result.accepted
    assert not dtype_result.accepted
    assert not trailing_result.accepted
    assert SecurityDiagnosticCode.CHUNK_METADATA_INVALID in shape_result.codes
    assert SecurityDiagnosticCode.CHUNK_METADATA_INVALID in dtype_result.codes
    assert SecurityDiagnosticCode.CHUNK_METADATA_INVALID in trailing_result.codes


def test_s022_npy_decoder_rejects_header_element_and_decoded_byte_limits():
    payload = _npy_bytes(np.zeros((2, 2), dtype=np.float32))
    large = _npy_bytes(np.zeros((4, 4), dtype=np.float32))

    header_result = validate_s022_npy_decoder_payload(payload, _policy(max_header_bytes=4))
    element_result = validate_s022_npy_decoder_payload(large, _policy(expected_shape=(4, 4), max_elements=4))
    decoded_result = validate_s022_npy_decoder_payload(payload, _policy(max_decoded_bytes=4))

    assert not header_result.accepted
    assert not element_result.accepted
    assert not decoded_result.accepted
    assert SecurityDiagnosticCode.CHUNK_LIMIT_EXCEEDED in header_result.codes
    assert SecurityDiagnosticCode.CHUNK_LIMIT_EXCEEDED in element_result.codes
    assert SecurityDiagnosticCode.DECOMPRESSION_LIMIT_EXCEEDED in decoded_result.codes
