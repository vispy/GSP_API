"""Virtual data-source models and local tiled-image proof helpers."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from math import ceil
from typing import Any

import numpy as np
import numpy.typing as npt

from .extensions import ExtensionKind, ExtensionManifest, TILED_IMAGE_EXTENSION_ID, TILED_IMAGE_EXTENSION_VERSION
from .ids import validate_id


class DataSourceKind(str, Enum):
    """Known v0.1 data-source kinds."""

    EAGER_IMAGE = "eager-image"
    TILED_IMAGE = "tiled-image"
    VIRTUAL_IMAGE = "virtual-image"
    OPAQUE = "opaque"


class DataLocality(str, Enum):
    """Where a virtual data source is materialized from."""

    IN_MEMORY = "in-memory"
    LOCAL_FILE = "local-file"
    CLIENT_FETCH = "client-fetch"
    SERVER_FETCH = "server-fetch"
    REMOTE_HANDLE = "remote-handle"
    SYNTHETIC = "synthetic"


class CredentialPolicy(str, Enum):
    """Credential policy declared by a data source."""

    NONE = "none"
    PRECONFIGURED = "preconfigured"
    FORBIDDEN = "forbidden"


class MaterializationPolicy(str, Enum):
    """How a backend may materialize source data."""

    FULL = "full"
    TILE = "tile"
    VIEWPORT_MOSAIC = "viewport-mosaic"
    UNSUPPORTED = "unsupported"


class TileEncoding(str, Enum):
    """Tile payload encoding."""

    ARRAY = "array"
    PNG = "png"
    JPEG = "jpeg"
    RAW = "raw"


class TileAvailability(str, Enum):
    """Whether the tile set is complete."""

    COMPLETE = "complete"
    PARTIAL = "partial"
    UNKNOWN = "unknown"


class TileStatus(str, Enum):
    """Status for one tile request."""

    OK = "ok"
    MISSING = "missing"
    UNSUPPORTED = "unsupported"
    FAILED = "failed"


@dataclass(frozen=True, slots=True)
class DataSourceDescriptor:
    """Core protocol descriptor for virtual data sources."""

    id: str
    kind: DataSourceKind
    extension_id: str | None = None
    extension_version: str | None = None
    shape: tuple[int, ...] = ()
    dtype: str = "uint8"
    channels: int = 1
    coordinate_system: str = "pixel"
    extent: tuple[float, float, float, float] | None = None
    origin: str = "upper"
    locality: DataLocality = DataLocality.IN_MEMORY
    credential_policy: CredentialPolicy = CredentialPolicy.NONE
    materialization_policy: MaterializationPolicy = MaterializationPolicy.FULL
    metadata: dict[str, Any] | None = None

    def __post_init__(self) -> None:
        validate_id(self.id)
        if not self.shape:
            raise ValueError("data-source shape must not be empty")
        if any(dim <= 0 for dim in self.shape):
            raise ValueError("data-source shape dimensions must be positive")
        if not self.dtype:
            raise ValueError("data-source dtype must not be empty")
        if self.channels <= 0:
            raise ValueError("channels must be positive")
        if self.origin not in ("upper", "lower"):
            raise ValueError("origin must be upper or lower")


@dataclass(frozen=True, slots=True)
class TileIndex:
    """Tile coordinate; x is column, y is row."""

    level: int
    x: int
    y: int

    def __post_init__(self) -> None:
        if self.level < 0:
            raise ValueError("tile level must be non-negative")
        if self.x < 0 or self.y < 0:
            raise ValueError("tile x/y must be non-negative")


@dataclass(frozen=True, slots=True)
class TiledImageSource:
    """Built-in v0.1 tiled image source descriptor."""

    id: str
    shape: tuple[int, ...]
    tile_shape: tuple[int, int]
    levels: int = 1
    level_downsample: tuple[int, ...] = (1,)
    dtype: str = "uint8"
    channels: int = 4
    extent: tuple[float, float, float, float] | None = None
    origin: str = "upper"
    encoding: TileEncoding = TileEncoding.ARRAY
    availability: TileAvailability = TileAvailability.COMPLETE
    locality: DataLocality = DataLocality.SYNTHETIC
    credential_policy: CredentialPolicy = CredentialPolicy.NONE
    materialization_policy: MaterializationPolicy = MaterializationPolicy.VIEWPORT_MOSAIC
    max_tiles_per_request: int = 256
    missing_tile_policy: str = "transparent"
    extension_id: str = TILED_IMAGE_EXTENSION_ID
    extension_version: str = TILED_IMAGE_EXTENSION_VERSION

    def __post_init__(self) -> None:
        validate_id(self.id)
        if len(self.shape) not in (2, 3):
            raise ValueError("tiled image shape must be (H, W) or (H, W, C)")
        if any(dim <= 0 for dim in self.shape):
            raise ValueError("tiled image shape dimensions must be positive")
        if self.tile_shape[0] <= 0 or self.tile_shape[1] <= 0:
            raise ValueError("tile_shape dimensions must be positive")
        if self.levels <= 0:
            raise ValueError("levels must be positive")
        if len(self.level_downsample) != self.levels:
            raise ValueError("level_downsample length must match levels")
        if any(scale <= 0 for scale in self.level_downsample):
            raise ValueError("level_downsample values must be positive")
        if self.channels <= 0:
            raise ValueError("channels must be positive")
        if self.credential_policy != CredentialPolicy.NONE:
            raise ValueError("executable v0.1 tiled image proof requires credential_policy=none")
        if self.locality not in (DataLocality.SYNTHETIC, DataLocality.IN_MEMORY):
            raise ValueError("executable v0.1 tiled image proof supports only synthetic/in-memory locality")
        if self.origin not in ("upper", "lower"):
            raise ValueError("origin must be upper or lower")

    def descriptor(self) -> DataSourceDescriptor:
        """Return the core descriptor view of this tiled source."""
        return DataSourceDescriptor(
            id=self.id,
            kind=DataSourceKind.TILED_IMAGE,
            extension_id=self.extension_id,
            extension_version=self.extension_version,
            shape=self.shape,
            dtype=self.dtype,
            channels=self.channels,
            extent=self.extent,
            origin=self.origin,
            locality=self.locality,
            credential_policy=self.credential_policy,
            materialization_policy=self.materialization_policy,
            metadata={"tile_shape": self.tile_shape, "levels": self.levels},
        )

    def validate_manifest_link(self, manifest: ExtensionManifest) -> None:
        """Validate that this source is linked to a compatible static extension manifest."""
        validate_tiled_image_source_manifest_link(self, manifest)

    def shape_for_level(self, level: int) -> tuple[int, int]:
        """Return level-local image height and width."""
        if level < 0 or level >= self.levels:
            raise ValueError("level is outside source levels")
        scale = self.level_downsample[level]
        return (ceil(self.shape[0] / scale), ceil(self.shape[1] / scale))


@dataclass(frozen=True, slots=True)
class TileRequest:
    """Request one tile from a tiled image source."""

    source_id: str
    tile: TileIndex
    source_rect: tuple[int, int, int, int] | None = None
    requested_dtype: str | None = None
    requested_channels: int | None = None

    def __post_init__(self) -> None:
        validate_id(self.source_id)


@dataclass(frozen=True, slots=True)
class TileResult:
    """Result for one local in-process tile request."""

    source_id: str
    tile: TileIndex
    status: TileStatus
    data: npt.NDArray[np.uint8] | None = None
    shape: tuple[int, ...] = ()
    dtype: str = ""
    source_rect: tuple[int, int, int, int] | None = None
    diagnostic: str | None = None

    def __post_init__(self) -> None:
        validate_id(self.source_id)
        if self.status == TileStatus.OK and self.data is None:
            raise ValueError("ok tile results require data")
        if self.status != TileStatus.OK and not self.diagnostic:
            raise ValueError("non-ok tile results require a diagnostic")


@dataclass(frozen=True, slots=True)
class ViewportTileRequest:
    """Request a deterministic source-rectangle mosaic."""

    source_id: str
    level: int
    source_rect: tuple[int, int, int, int]
    output_shape: tuple[int, int] | None = None

    def __post_init__(self) -> None:
        validate_id(self.source_id)
        x, y, width, height = self.source_rect
        if width <= 0 or height <= 0:
            raise ValueError("source_rect must be x, y, width, height with positive size")
        if self.level < 0:
            raise ValueError("level must be non-negative")
        if self.output_shape is not None and (self.output_shape[0] <= 0 or self.output_shape[1] <= 0):
            raise ValueError("output_shape dimensions must be positive")


@dataclass(frozen=True, slots=True)
class ViewportMosaicResult:
    """Materialized local mosaic for a viewport/source rectangle."""

    source_id: str
    level: int
    source_rect: tuple[int, int, int, int]
    data: npt.NDArray[np.uint8]
    tile_indices: tuple[TileIndex, ...]
    diagnostic: str | None = None

    def __post_init__(self) -> None:
        validate_id(self.source_id)
        if self.data.ndim not in (2, 3):
            raise ValueError("mosaic data must have 2 or 3 dimensions")


@dataclass(frozen=True, slots=True)
class TiledImageQueryPayload:
    """Typed extension payload for tiled-image query hits."""

    source_id: str
    level: int
    tile_x: int
    tile_y: int
    texel_x: int
    texel_y: int
    source_x: int
    source_y: int
    uv: tuple[float, float] | None = None
    value: tuple[int, ...] | int | None = None

    def __post_init__(self) -> None:
        validate_id(self.source_id)


class FakeTiledImageProvider:
    """Deterministic in-memory tiled image provider for reference tests."""

    def __init__(self, source: TiledImageSource):
        self.source = source

    def get_tile(self, request: TileRequest) -> TileResult:
        """Return one deterministic tile as a direct NumPy array."""
        if request.source_id != self.source.id:
            return TileResult(
                source_id=request.source_id,
                tile=request.tile,
                status=TileStatus.FAILED,
                diagnostic=f"provider source {self.source.id!r} cannot serve {request.source_id!r}",
            )
        height, width = self.source.shape_for_level(request.tile.level)
        tile_h, tile_w = self.source.tile_shape
        x0 = request.tile.x * tile_w
        y0 = request.tile.y * tile_h
        if x0 >= width or y0 >= height:
            return TileResult(
                source_id=request.source_id,
                tile=request.tile,
                status=TileStatus.MISSING,
                diagnostic="tile is outside source bounds",
            )

        out_w = min(tile_w, width - x0)
        out_h = min(tile_h, height - y0)
        data = self._pixels(request.tile.level, x0, y0, out_w, out_h)
        return TileResult(
            source_id=request.source_id,
            tile=request.tile,
            status=TileStatus.OK,
            data=data,
            shape=data.shape,
            dtype=str(data.dtype),
            source_rect=(x0, y0, out_w, out_h),
        )

    def get_viewport_mosaic(self, request: ViewportTileRequest) -> ViewportMosaicResult:
        """Materialize a deterministic source-rectangle mosaic."""
        if request.source_id != self.source.id:
            raise ValueError(f"provider source {self.source.id!r} cannot serve {request.source_id!r}")
        height, width = self.source.shape_for_level(request.level)
        x0, y0, out_w, out_h = _clip_rect(request.source_rect, width, height)
        if out_w <= 0 or out_h <= 0:
            raise ValueError("source_rect does not intersect source bounds")

        tile_h, tile_w = self.source.tile_shape
        x_first, x_last = x0 // tile_w, (x0 + out_w - 1) // tile_w
        y_first, y_last = y0 // tile_h, (y0 + out_h - 1) // tile_h
        tile_indices = tuple(
            TileIndex(request.level, tile_x, tile_y)
            for tile_y in range(y_first, y_last + 1)
            for tile_x in range(x_first, x_last + 1)
        )
        if len(tile_indices) > self.source.max_tiles_per_request:
            raise ValueError("viewport mosaic exceeds max_tiles_per_request")

        data = self._pixels(request.level, x0, y0, out_w, out_h)
        return ViewportMosaicResult(
            source_id=request.source_id,
            level=request.level,
            source_rect=(x0, y0, out_w, out_h),
            data=data,
            tile_indices=tile_indices,
        )

    def pixel_value(self, level: int, source_x: int, source_y: int) -> tuple[int, int, int, int]:
        """Return the deterministic RGBA value for one level-local source pixel."""
        return (
            source_x % 256,
            source_y % 256,
            level % 256,
            255,
        )

    def _pixels(self, level: int, x0: int, y0: int, width: int, height: int) -> npt.NDArray[np.uint8]:
        xs = (np.arange(x0, x0 + width, dtype=np.uint16) % 256).astype(np.uint8)
        ys = (np.arange(y0, y0 + height, dtype=np.uint16) % 256).astype(np.uint8)
        data = np.zeros((height, width, 4), dtype=np.uint8)
        data[..., 0] = xs[None, :]
        data[..., 1] = ys[:, None]
        data[..., 2] = level % 256
        data[..., 3] = 255
        return data


def _clip_rect(rect: tuple[int, int, int, int], width: int, height: int) -> tuple[int, int, int, int]:
    x, y, rect_w, rect_h = rect
    x0 = max(0, x)
    y0 = max(0, y)
    x1 = min(width, x + rect_w)
    y1 = min(height, y + rect_h)
    return x0, y0, max(0, x1 - x0), max(0, y1 - y0)


def validate_tiled_image_source_manifest_link(source: TiledImageSource, manifest: ExtensionManifest) -> None:
    """Validate static manifest linkage for the built-in tiled-image source proof."""
    if manifest.kind != ExtensionKind.DATA_SOURCE:
        raise ValueError("tiled image source requires a data-source extension manifest")
    if source.extension_id != manifest.id:
        raise ValueError("tiled image source extension_id does not match manifest id")
    if source.extension_version != manifest.version:
        raise ValueError("tiled image source extension_version does not match manifest version")
    if manifest.schema.get("source_kind") != DataSourceKind.TILED_IMAGE.value:
        raise ValueError("tiled image manifest schema must declare source_kind='tiled-image'")
    if manifest.schema.get("credential_policy") != CredentialPolicy.NONE.value:
        raise ValueError("tiled image manifest schema must declare credential_policy='none'")
