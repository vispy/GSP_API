"""Resource models for the GSP data plane."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from .ids import validate_id


class ResourceUsage(str, Enum):
    """Intended use of a resource."""

    ATTRIBUTE = "attribute"
    INDEX = "index"
    UNIFORM = "uniform"
    TEXTURE = "texture"
    READBACK = "readback"


class ResourceMutability(str, Enum):
    """Mutation policy for a resource."""

    IMMUTABLE = "immutable"
    DYNAMIC = "dynamic"
    STREAM = "stream"


class ResourceLocality(str, Enum):
    """Where resource bytes live initially."""

    CLIENT_MEMORY = "client-memory"
    SERVER_MEMORY = "server-memory"
    EXTERNAL = "external"


@dataclass(frozen=True, slots=True)
class BufferResource:
    """Contiguous v0.1 buffer resource descriptor.

    `data` may hold a memoryview for the in-process fast path. Debug JSON and
    remote transports should use their own encoding instead of relying on it.
    """

    id: str
    dtype: str
    shape: tuple[int, ...]
    byte_length: int
    usage: tuple[ResourceUsage, ...]
    mutability: ResourceMutability = ResourceMutability.IMMUTABLE
    locality: ResourceLocality = ResourceLocality.CLIENT_MEMORY
    contiguous: bool = True
    data: memoryview | None = None
    external_source: str | None = None
    metadata: dict[str, Any] | None = None

    def __post_init__(self) -> None:
        validate_id(self.id)
        if not self.dtype:
            raise ValueError("dtype must not be empty")
        if not self.shape:
            raise ValueError("shape must not be empty")
        if any(dim < 0 for dim in self.shape):
            raise ValueError("shape dimensions must be non-negative")
        if self.byte_length < 0:
            raise ValueError("byte_length must be non-negative")
        if not self.usage:
            raise ValueError("at least one resource usage is required")
        if not self.contiguous:
            raise ValueError("M002 protocol spine supports only contiguous buffers")
        if self.data is not None and self.data.nbytes != self.byte_length:
            raise ValueError("data byte length does not match byte_length")
        if self.locality == ResourceLocality.EXTERNAL and not self.external_source:
            raise ValueError("external resources require external_source")


@dataclass(frozen=True, slots=True)
class AttributeSource:
    """Reference to attribute data inside a buffer resource."""

    resource_id: str
    dtype: str
    shape: tuple[int, ...]
    offset_bytes: int = 0
    stride_bytes: int | None = None

    def __post_init__(self) -> None:
        validate_id(self.resource_id)
        if not self.dtype:
            raise ValueError("dtype must not be empty")
        if not self.shape:
            raise ValueError("shape must not be empty")
        if any(dim < 0 for dim in self.shape):
            raise ValueError("shape dimensions must be non-negative")
        if self.offset_bytes < 0:
            raise ValueError("offset_bytes must be non-negative")
        if self.stride_bytes is not None and self.stride_bytes <= 0:
            raise ValueError("stride_bytes must be positive when provided")
