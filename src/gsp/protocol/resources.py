"""Resource models for the GSP data plane."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from enum import Enum
from typing import Any

import numpy as np
import numpy.typing as npt

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


class Texture2DFormat(str, Enum):
    """Accepted protocol texture formats."""

    RGBA8 = "rgba8"


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
class Texture2D:
    """Immutable S050 RGBA8 texture value resource."""

    id: str
    image: npt.NDArray[np.uint8]
    format: Texture2DFormat = Texture2DFormat.RGBA8

    def __post_init__(self) -> None:
        validate_id(self.id)
        if not isinstance(self.format, Texture2DFormat):
            raise TypeError("texture2d_invalid_resource: format must be a Texture2DFormat")
        if self.format is not Texture2DFormat.RGBA8:
            raise ValueError("texture2d_invalid_resource: only rgba8 is accepted")
        if not isinstance(self.image, np.ndarray):
            raise TypeError("texture2d_invalid_resource: image must be a numpy array")
        if self.image.dtype != np.dtype(np.uint8):
            raise TypeError("texture2d_invalid_resource: image must have dtype uint8")
        if self.image.ndim != 3 or self.image.shape[2] != 4:
            raise ValueError(
                "texture2d_invalid_resource: image must have shape (H, W, 4)"
            )
        if self.image.shape[0] <= 0 or self.image.shape[1] <= 0:
            raise ValueError(
                "texture2d_invalid_resource: image dimensions must be positive"
            )
        if not self.image.flags.c_contiguous:
            raise ValueError("texture2d_invalid_resource: image must be contiguous")


def validate_texture2d_resources(textures: Sequence[Texture2D]) -> dict[str, Texture2D]:
    """Validate a collection of Texture2D resources and return it by id."""
    texture_map: dict[str, Texture2D] = {}
    for texture in textures:
        if not isinstance(texture, Texture2D):
            raise TypeError("texture2d_invalid_resource: expected Texture2D")
        if texture.id in texture_map:
            raise ValueError(f"texture2d_invalid_resource: duplicate id {texture.id!r}")
        texture_map[texture.id] = texture
    return texture_map


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
