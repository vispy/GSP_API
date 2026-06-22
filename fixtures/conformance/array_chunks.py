"""Validation for first-slice conformance fixture array chunks."""

from __future__ import annotations

import base64
import binascii
import hashlib
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Final, TypeAlias, cast

from gsp.protocol.ids import validate_id


RawArrayChunk: TypeAlias = Mapping[str, object]

_REQUIRED_FIELDS: Final = (
    "resource_id",
    "array_id",
    "semantic_role",
    "dtype",
    "shape",
    "byte_order",
    "memory_order",
    "encoding",
    "compression",
    "byte_length",
    "checksum",
    "data_base64",
)
_DTYPE_ITEMSIZE: Final = {"float32": 4, "uint8": 1}
_SHA256_HEX_LENGTH: Final = 64


@dataclass(frozen=True, slots=True)
class Base64ArrayChunk:
    """Validated first-slice eager array chunk."""

    resource_id: str
    array_id: str
    semantic_role: str
    dtype: str
    shape: tuple[int, ...]
    byte_order: str
    memory_order: str
    encoding: str
    compression: str
    byte_length: int
    checksum_algorithm: str
    checksum_scope: str
    checksum_value: str
    decoded_bytes: bytes


def validate_base64_array_chunk(raw: RawArrayChunk) -> Base64ArrayChunk:
    """Validate a `gsp.conformance.fixture@0.1` inline base64 array chunk."""
    _require_fields(raw)
    resource_id = _required_id(raw, "resource_id")
    array_id = _required_id(raw, "array_id")
    semantic_role = _required_string(raw, "semantic_role")
    dtype = _required_string(raw, "dtype")
    if dtype not in _DTYPE_ITEMSIZE:
        raise ValueError(f"unsupported array dtype: {dtype!r}")

    shape = _required_shape(raw, "shape")
    byte_order = _required_string(raw, "byte_order")
    _validate_byte_order(dtype, byte_order)
    memory_order = _required_string(raw, "memory_order")
    if memory_order != "C":
        raise ValueError("first-slice array chunks require memory_order='C'")

    encoding = _required_string(raw, "encoding")
    if encoding != "base64":
        raise ValueError("first-slice replayable array chunks require encoding='base64'")
    compression = _required_string(raw, "compression")
    if compression != "none":
        raise ValueError("first-slice array chunks require compression='none'")

    byte_length = _required_nonnegative_int(raw, "byte_length")
    expected_byte_length = _shape_product(shape) * _DTYPE_ITEMSIZE[dtype]
    if byte_length != expected_byte_length:
        raise ValueError(f"byte_length {byte_length} does not match dtype/shape byte length {expected_byte_length}")

    checksum = _required_checksum(raw)
    data_base64 = _required_string(raw, "data_base64")
    decoded = _decode_base64(data_base64)
    if len(decoded) != byte_length:
        raise ValueError(f"decoded byte length {len(decoded)} does not match byte_length {byte_length}")

    digest = hashlib.sha256(decoded).hexdigest()
    if digest != checksum["value"]:
        raise ValueError("decoded bytes do not match SHA-256 checksum")

    return Base64ArrayChunk(
        resource_id=resource_id,
        array_id=array_id,
        semantic_role=semantic_role,
        dtype=dtype,
        shape=shape,
        byte_order=byte_order,
        memory_order=memory_order,
        encoding=encoding,
        compression=compression,
        byte_length=byte_length,
        checksum_algorithm=checksum["algorithm"],
        checksum_scope=checksum["scope"],
        checksum_value=checksum["value"],
        decoded_bytes=decoded,
    )


def _require_fields(raw: RawArrayChunk) -> None:
    missing = tuple(field for field in _REQUIRED_FIELDS if field not in raw)
    if missing:
        raise ValueError(f"array chunk is missing required fields: {missing}")


def _required_id(raw: RawArrayChunk, field_name: str) -> str:
    return validate_id(_required_string(raw, field_name))


def _required_string(raw: RawArrayChunk, field_name: str) -> str:
    value = raw[field_name]
    if not isinstance(value, str) or not value:
        raise ValueError(f"{field_name} must be a non-empty string")
    return value


def _required_nonnegative_int(raw: RawArrayChunk, field_name: str) -> int:
    value = raw[field_name]
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise ValueError(f"{field_name} must be a non-negative integer")
    return value


def _required_shape(raw: RawArrayChunk, field_name: str) -> tuple[int, ...]:
    value = raw[field_name]
    if isinstance(value, (str, bytes)) or not isinstance(value, Sequence):
        raise ValueError(f"{field_name} must be a sequence of non-negative integers")
    shape = tuple(cast(Sequence[object], value))
    if not shape:
        raise ValueError("shape must not be empty")
    if any(not isinstance(dim, int) or isinstance(dim, bool) or dim < 0 for dim in shape):
        raise ValueError("shape must contain only non-negative integers")
    return cast(tuple[int, ...], shape)


def _shape_product(shape: tuple[int, ...]) -> int:
    product = 1
    for dim in shape:
        product *= dim
    return product


def _validate_byte_order(dtype: str, byte_order: str) -> None:
    if dtype == "uint8":
        if byte_order != "not-applicable":
            raise ValueError("uint8 array chunks require byte_order='not-applicable'")
        return
    if byte_order != "little":
        raise ValueError("first-slice multi-byte array chunks require byte_order='little'")


def _required_checksum(raw: RawArrayChunk) -> dict[str, str]:
    value = raw["checksum"]
    if not isinstance(value, Mapping):
        raise ValueError("checksum must be an object")
    checksum = cast(Mapping[str, object], value)
    algorithm = checksum.get("algorithm")
    scope = checksum.get("scope")
    digest = checksum.get("value")
    if algorithm != "sha256":
        raise ValueError("checksum.algorithm must be 'sha256'")
    if scope != "decoded_uncompressed_bytes":
        raise ValueError("checksum.scope must be 'decoded_uncompressed_bytes'")
    if not isinstance(digest, str) or len(digest) != _SHA256_HEX_LENGTH or digest.lower() != digest:
        raise ValueError("checksum.value must be a lowercase SHA-256 hex digest")
    try:
        int(digest, 16)
    except ValueError as exc:
        raise ValueError("checksum.value must be a lowercase SHA-256 hex digest") from exc
    return {"algorithm": "sha256", "scope": "decoded_uncompressed_bytes", "value": digest}


def _decode_base64(value: str) -> bytes:
    try:
        return base64.b64decode(value.encode("ascii"), validate=True)
    except (binascii.Error, UnicodeEncodeError) as exc:
        raise ValueError("data_base64 must be standard base64 without invalid characters") from exc
