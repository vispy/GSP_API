"""No-network decoder policy validation helpers."""

from __future__ import annotations

import ast
from dataclasses import dataclass
from math import prod
from typing import Any

import numpy as np

from .security import SecurityDiagnostic, SecurityDiagnosticCode, SecurityValidationResult


S022_NPY_DECODER_ID = "gsp.decoder.npy.v1"
S022_NPY_ALLOWED_DTYPES = ("uint8", "uint16", "float32")
S022_NPY_ALLOWED_VERSIONS = ((1, 0), (2, 0))


@dataclass(frozen=True, slots=True)
class S022NpyDecoderPolicy:
    """Bounds and expected contract for the trusted S022 `.npy` decoder."""

    expected_shape: tuple[int, ...]
    expected_dtype: str
    allowed_dtypes: tuple[str, ...] = S022_NPY_ALLOWED_DTYPES
    allowed_versions: tuple[tuple[int, int], ...] = S022_NPY_ALLOWED_VERSIONS
    max_header_bytes: int = 4096
    max_rank: int = 3
    max_elements: int = 1_048_576
    max_decoded_bytes: int = 4_194_304
    allow_fortran_order: bool = False

    def __post_init__(self) -> None:
        """Validate policy bounds without inspecting any payload."""
        if not self.expected_shape:
            raise ValueError("expected_shape must not be empty")
        if any(dim <= 0 for dim in self.expected_shape):
            raise ValueError("expected_shape dimensions must be positive")
        if not self.expected_dtype:
            raise ValueError("expected_dtype must not be empty")
        if self.max_header_bytes <= 0:
            raise ValueError("max_header_bytes must be positive")
        if self.max_rank <= 0:
            raise ValueError("max_rank must be positive")
        if self.max_elements <= 0:
            raise ValueError("max_elements must be positive")
        if self.max_decoded_bytes <= 0:
            raise ValueError("max_decoded_bytes must be positive")


@dataclass(frozen=True, slots=True)
class S022NpyHeader:
    """Validated `.npy` header metadata."""

    version: tuple[int, int]
    shape: tuple[int, ...]
    dtype: str
    data_offset: int
    decoded_bytes: int


@dataclass(frozen=True, slots=True)
class S022NpyDecoderValidationResult:
    """Result of validating S022 `.npy` decoder policy."""

    accepted: bool
    header: S022NpyHeader | None = None
    diagnostics: tuple[SecurityDiagnostic, ...] = ()

    def __post_init__(self) -> None:
        """Validate consistency between acceptance, header metadata, and diagnostics."""
        if self.accepted:
            if self.header is None:
                raise ValueError("accepted .npy decoder validation requires header metadata")
            if self.diagnostics:
                raise ValueError("accepted .npy decoder validation must not carry diagnostics")
        elif not self.diagnostics:
            raise ValueError("rejected .npy decoder validation requires diagnostics")

    @property
    def codes(self) -> tuple[SecurityDiagnosticCode, ...]:
        """Return diagnostic codes for assertions and fixture expectations."""
        return tuple(diagnostic.code for diagnostic in self.diagnostics)

    def as_security_result(self) -> SecurityValidationResult:
        """Return the validation result as a generic security validation result."""
        return SecurityValidationResult(self.accepted, self.diagnostics)


def validate_s022_npy_decoder_payload(
    payload: bytes,
    policy: S022NpyDecoderPolicy,
) -> S022NpyDecoderValidationResult:
    """Validate S022 `.npy` bytes without materializing an array."""
    diagnostics: list[SecurityDiagnostic] = []
    parsed = _parse_npy_header(payload, policy, diagnostics)
    if parsed is None:
        return S022NpyDecoderValidationResult(False, diagnostics=tuple(diagnostics))

    version, header, data_offset = parsed
    dtype = _dtype_from_header(header.get("descr"), diagnostics)
    shape = _shape_from_header(header.get("shape"), diagnostics)
    fortran_order = header.get("fortran_order")
    if fortran_order is not False and not policy.allow_fortran_order:
        diagnostics.append(SecurityDiagnostic(SecurityDiagnosticCode.CHUNK_METADATA_INVALID, "S022 .npy decoder requires fortran_order=false"))

    if dtype is not None:
        _validate_dtype(dtype, policy, diagnostics)
    if shape is not None:
        _validate_shape(shape, policy, diagnostics)

    if dtype is not None and shape is not None:
        decoded_bytes = prod(shape) * dtype.itemsize
        _validate_payload_size(payload, data_offset, decoded_bytes, policy, diagnostics)
    else:
        decoded_bytes = 0

    if diagnostics:
        return S022NpyDecoderValidationResult(False, diagnostics=tuple(diagnostics))
    return S022NpyDecoderValidationResult(
        True,
        header=S022NpyHeader(
            version=version,
            shape=shape or (),
            dtype=(dtype.name if dtype is not None else ""),
            data_offset=data_offset,
            decoded_bytes=decoded_bytes,
        ),
    )


def _parse_npy_header(
    payload: bytes,
    policy: S022NpyDecoderPolicy,
    diagnostics: list[SecurityDiagnostic],
) -> tuple[tuple[int, int], dict[str, Any], int] | None:
    if not payload.startswith(b"\x93NUMPY"):
        diagnostics.append(SecurityDiagnostic(SecurityDiagnosticCode.CHUNK_METADATA_INVALID, "invalid .npy magic prefix"))
        return None
    if len(payload) < 10:
        diagnostics.append(SecurityDiagnostic(SecurityDiagnosticCode.CHUNK_METADATA_INVALID, ".npy payload is too short"))
        return None
    version = (payload[6], payload[7])
    if version not in policy.allowed_versions:
        diagnostics.append(SecurityDiagnostic(SecurityDiagnosticCode.CHUNK_METADATA_INVALID, f".npy version {version!r} is not allowed"))
        return None
    length_size = 2 if version == (1, 0) else 4
    length_offset = 8
    header_offset = length_offset + length_size
    if len(payload) < header_offset:
        diagnostics.append(SecurityDiagnostic(SecurityDiagnosticCode.CHUNK_METADATA_INVALID, ".npy payload is missing header length"))
        return None
    header_length = int.from_bytes(payload[length_offset:header_offset], "little")
    if header_length > policy.max_header_bytes:
        diagnostics.append(SecurityDiagnostic(SecurityDiagnosticCode.CHUNK_LIMIT_EXCEEDED, ".npy header exceeds max_header_bytes"))
        return None
    data_offset = header_offset + header_length
    if len(payload) < data_offset:
        diagnostics.append(SecurityDiagnostic(SecurityDiagnosticCode.CHUNK_METADATA_INVALID, ".npy payload is shorter than declared header"))
        return None
    header_bytes = payload[header_offset:data_offset]
    try:
        header_text = header_bytes.decode("latin1" if version == (1, 0) else "utf-8").strip()
        header_value = ast.literal_eval(header_text)
    except (SyntaxError, ValueError, UnicodeDecodeError) as exc:
        diagnostics.append(SecurityDiagnostic(SecurityDiagnosticCode.CHUNK_METADATA_INVALID, f".npy header parse failed: {exc}"))
        return None
    if not isinstance(header_value, dict):
        diagnostics.append(SecurityDiagnostic(SecurityDiagnosticCode.CHUNK_METADATA_INVALID, ".npy header must be a dictionary"))
        return None
    header = {str(key): value for key, value in header_value.items()}
    if set(header) != {"descr", "fortran_order", "shape"}:
        diagnostics.append(SecurityDiagnostic(SecurityDiagnosticCode.CHUNK_METADATA_INVALID, ".npy header has unexpected keys"))
        return None
    return version, header, data_offset


def _dtype_from_header(value: object, diagnostics: list[SecurityDiagnostic]) -> np.dtype[Any] | None:
    if not isinstance(value, str):
        diagnostics.append(SecurityDiagnostic(SecurityDiagnosticCode.CHUNK_METADATA_INVALID, ".npy descr must be a string"))
        return None
    try:
        dtype = np.dtype(value)
    except TypeError as exc:
        diagnostics.append(SecurityDiagnostic(SecurityDiagnosticCode.CHUNK_METADATA_INVALID, f".npy dtype is invalid: {exc}"))
        return None
    return dtype


def _shape_from_header(value: object, diagnostics: list[SecurityDiagnostic]) -> tuple[int, ...] | None:
    if not isinstance(value, tuple) or not value:
        diagnostics.append(SecurityDiagnostic(SecurityDiagnosticCode.CHUNK_METADATA_INVALID, ".npy shape must be a non-empty tuple"))
        return None
    if not all(isinstance(dim, int) and dim > 0 for dim in value):
        diagnostics.append(SecurityDiagnostic(SecurityDiagnosticCode.CHUNK_METADATA_INVALID, ".npy shape dimensions must be positive integers"))
        return None
    return tuple(value)


def _validate_dtype(
    dtype: np.dtype[Any],
    policy: S022NpyDecoderPolicy,
    diagnostics: list[SecurityDiagnostic],
) -> None:
    if dtype.name not in policy.allowed_dtypes:
        diagnostics.append(SecurityDiagnostic(SecurityDiagnosticCode.CHUNK_METADATA_INVALID, f".npy dtype {dtype.name!r} is not allowed"))
    if dtype.hasobject or dtype.kind == "O":
        diagnostics.append(SecurityDiagnostic(SecurityDiagnosticCode.CHUNK_METADATA_INVALID, ".npy object dtype and pickle payloads are rejected"))
    if dtype.fields is not None:
        diagnostics.append(SecurityDiagnostic(SecurityDiagnosticCode.CHUNK_METADATA_INVALID, ".npy structured dtype is rejected"))
    if dtype.kind in ("S", "U", "V"):
        diagnostics.append(SecurityDiagnostic(SecurityDiagnosticCode.CHUNK_METADATA_INVALID, ".npy string, unicode, and void dtypes are rejected"))
    if dtype.byteorder == ">":
        diagnostics.append(SecurityDiagnostic(SecurityDiagnosticCode.CHUNK_METADATA_INVALID, ".npy big-endian dtype is rejected"))
    if dtype.name != policy.expected_dtype:
        diagnostics.append(SecurityDiagnostic(SecurityDiagnosticCode.CHUNK_METADATA_INVALID, ".npy dtype does not match expected dtype"))


def _validate_shape(
    shape: tuple[int, ...],
    policy: S022NpyDecoderPolicy,
    diagnostics: list[SecurityDiagnostic],
) -> None:
    if len(shape) > policy.max_rank:
        diagnostics.append(SecurityDiagnostic(SecurityDiagnosticCode.CHUNK_METADATA_INVALID, ".npy rank exceeds max_rank"))
    if shape != policy.expected_shape:
        diagnostics.append(SecurityDiagnostic(SecurityDiagnosticCode.CHUNK_METADATA_INVALID, ".npy shape does not match expected shape"))
    elements = prod(shape)
    if elements > policy.max_elements:
        diagnostics.append(SecurityDiagnostic(SecurityDiagnosticCode.CHUNK_LIMIT_EXCEEDED, ".npy element count exceeds max_elements"))


def _validate_payload_size(
    payload: bytes,
    data_offset: int,
    decoded_bytes: int,
    policy: S022NpyDecoderPolicy,
    diagnostics: list[SecurityDiagnostic],
) -> None:
    if decoded_bytes > policy.max_decoded_bytes:
        diagnostics.append(SecurityDiagnostic(SecurityDiagnosticCode.DECOMPRESSION_LIMIT_EXCEEDED, ".npy decoded bytes exceed max_decoded_bytes"))
    expected_total = data_offset + decoded_bytes
    if len(payload) != expected_total:
        diagnostics.append(SecurityDiagnostic(SecurityDiagnosticCode.CHUNK_METADATA_INVALID, ".npy payload size does not match header shape and dtype"))
