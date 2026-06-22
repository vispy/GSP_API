"""Tests for first-slice conformance fixture array chunk validation."""

from __future__ import annotations

import base64
import hashlib

import pytest

from fixtures.conformance import validate_base64_array_chunk


def _chunk(decoded: bytes, *, dtype: str = "uint8", shape: list[int] | None = None) -> dict[str, object]:
    return {
        "resource_id": "res.points.colors",
        "array_id": "arr.points.colors.rgba8",
        "semantic_role": "point.colors.rgba8",
        "dtype": dtype,
        "shape": shape or [len(decoded)],
        "byte_order": "not-applicable" if dtype == "uint8" else "little",
        "memory_order": "C",
        "encoding": "base64",
        "compression": "none",
        "byte_length": len(decoded),
        "checksum": {
            "algorithm": "sha256",
            "scope": "decoded_uncompressed_bytes",
            "value": hashlib.sha256(decoded).hexdigest(),
        },
        "data_base64": base64.b64encode(decoded).decode("ascii"),
    }


def test_validate_uint8_base64_array_chunk_returns_decoded_bytes():
    decoded = bytes([255, 0, 0, 255])

    chunk = validate_base64_array_chunk(_chunk(decoded, shape=[1, 4]))

    assert chunk.resource_id == "res.points.colors"
    assert chunk.dtype == "uint8"
    assert chunk.shape == (1, 4)
    assert chunk.byte_order == "not-applicable"
    assert chunk.decoded_bytes == decoded


def test_validate_float32_base64_array_chunk_accepts_little_endian_bytes():
    decoded = b"\x00\x00\x80?\x00\x00\x00@"

    chunk = validate_base64_array_chunk(_chunk(decoded, dtype="float32", shape=[1, 2]))

    assert chunk.dtype == "float32"
    assert chunk.shape == (1, 2)
    assert chunk.byte_order == "little"
    assert chunk.byte_length == 8


@pytest.mark.parametrize(
    ("field", "message"),
    [
        ("resource_id", "missing required fields"),
        ("checksum", "missing required fields"),
        ("data_base64", "missing required fields"),
    ],
)
def test_validate_array_chunk_rejects_missing_required_fields(field: str, message: str):
    raw = _chunk(b"\x00")
    del raw[field]

    with pytest.raises(ValueError, match=message):
        validate_base64_array_chunk(raw)


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("dtype", "float64", "unsupported array dtype"),
        ("byte_order", "big", "byte_order"),
        ("memory_order", "F", "memory_order"),
        ("encoding", "omitted", "encoding='base64'"),
        ("compression", "zstd", "compression='none'"),
    ],
)
def test_validate_array_chunk_rejects_unsupported_first_slice_values(field: str, value: object, message: str):
    raw = _chunk(b"\x00")
    raw[field] = value

    with pytest.raises(ValueError, match=message):
        validate_base64_array_chunk(raw)


def test_validate_array_chunk_rejects_wrong_byte_length():
    raw = _chunk(b"\x00")
    raw["byte_length"] = 2

    with pytest.raises(ValueError, match="does not match dtype/shape"):
        validate_base64_array_chunk(raw)


def test_validate_array_chunk_rejects_decoded_length_mismatch():
    raw = _chunk(b"\x00", shape=[2])
    raw["byte_length"] = 2

    with pytest.raises(ValueError, match="decoded byte length"):
        validate_base64_array_chunk(raw)


def test_validate_array_chunk_rejects_wrong_checksum():
    raw = _chunk(b"\x00")
    raw["checksum"] = {
        "algorithm": "sha256",
        "scope": "decoded_uncompressed_bytes",
        "value": "0" * 64,
    }

    with pytest.raises(ValueError, match="SHA-256 checksum"):
        validate_base64_array_chunk(raw)


def test_validate_array_chunk_rejects_invalid_checksum_shape():
    raw = _chunk(b"\x00")
    raw["checksum"] = {
        "algorithm": "sha256",
        "scope": "decoded_uncompressed_bytes",
        "value": "ABC",
    }

    with pytest.raises(ValueError, match="lowercase SHA-256"):
        validate_base64_array_chunk(raw)


def test_validate_array_chunk_rejects_invalid_base64():
    raw = _chunk(b"\x00")
    raw["data_base64"] = "not base64!"

    with pytest.raises(ValueError, match="data_base64"):
        validate_base64_array_chunk(raw)
