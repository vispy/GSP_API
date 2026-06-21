I could not read the remote branch directly because GitHub reported no commit for `agentic-gsp-vispy2`; I am using the context you provided as the authority here. My recommendation below is designed to be pasted back into the repo as the ChatGPT Pro consultation result for M011.

---

# 1. Recommendation Summary

* Define a **minimal core `DataSourceDescriptor` abstraction** now, but implement only one built-in v0.1 source kind: `gsp.tiled-image.v0`.
* Treat **extensions as static manifests**, not dynamic plugins. In v0.1, an extension manifest is just a dataclass/dict registered explicitly by Python code or tests.
* Virtual data sources should be **both core and extension-aware**: the core protocol knows how to reference a data source, while specific source kinds can be declared by extension manifests.
* Implement a **local fake tiled image provider** only. No network fetch, cloud credentials, async streaming, cache eviction, package manager, or plugin loader.
* Represent data locality explicitly with a small enum: `in-memory`, `local-file`, `client-fetch`, `server-fetch`, `remote-handle`, `synthetic`.
* For v0.1 security, permit only `credential_policy="none"` and `credential_policy="preconfigured"` as declarative metadata. Do not store secrets, tokens, URLs with credentials, or executable fetch code in protocol objects.
* Matplotlib reference behavior should **materialize a viewport mosaic** from tiles using the fake provider. It may also materialize one requested tile in lower-level unit tests, but the renderer proof should validate a mosaic.
* Query for tiled images should return the same core image-style result fields plus tile metadata: `tile_level`, `tile_x`, `tile_y`, `texel`, `data_position`, `display_rgba`, and optionally scalar/vector value.
* Capabilities should advertise support for extension manifests and virtual data sources separately. Unsupported data-source kinds must adapt explicitly: `reject` or `unsupported` diagnostic, never silent fallback to eager image.
* The smallest proof is: create a synthetic tiled image pyramid in memory, render a viewport mosaic through Matplotlib, overlay existing point visual if useful, and query a point in the image to verify tile/texel/value mapping.

---

# 2. ADR Draft

## Title

ADR-0004 — Minimal GSP Extension and Virtual Data Source Model for v0.1

## Status

Proposed.

## Context

GSP v0.1 already has a stable vertical slice: protocol IDs, capability snapshots, contiguous in-process buffers, local transport without mandatory JSON/base64, `PointVisual`, `ImageVisual`, Matplotlib reference rendering, deterministic point-over-image query, a bounded Datoviz point/RGBA8 image adapter slice, and a minimal VisPy2 producer MVP.

The next architectural requirement is to support huge datasets without pretending they are ordinary eager buffers. Examples include tiled cloud images, microscopy pyramids, map tiles, point-cloud octrees, and remote simulation timesteps. However, v0.1 should not introduce a production plugin system, credential manager, network stack, cloud client, asynchronous scheduler, or Datoviz dependency.

## Decision

GSP v0.1 introduces:

1. a core `DataSourceDescriptor`;
2. a core `DataSourceRef`;
3. a static `ExtensionManifest` model;
4. a built-in minimal `TiledImageSource` source kind;
5. `TileRequest` and `TileResult` protocol models;
6. a local fake in-memory tile provider for tests and Matplotlib reference proof.

Virtual data sources are represented as protocol-level objects, while concrete source kinds may be declared through extension manifests. The first source kind, `gsp.tiled-image.v0`, is treated as a built-in reference extension. It is not loaded dynamically and does not require a plugin package manager.

The local in-process path remains primary. No JSON/base64 is required for execution. JSON remains acceptable for fixtures/debugging/replay.

## In scope

* Static extension manifest dataclasses or dictionaries.
* Core data-source descriptor and reference models.
* Built-in `gsp.tiled-image.v0` source kind.
* In-memory fake tiled provider.
* Matplotlib reference materialization of viewport mosaics.
* Query/readout for virtual tiled images in the reference path.
* Capability fields for virtual data and extension support.
* Explicit unsupported diagnostics for unsupported data-source kinds.

## Out of scope

* Dynamic plugin discovery.
* Python package entry-point loading.
* Runtime shader extension loading.
* Production cloud fetch.
* Real HTTP/S3/GCS/Zarr/OME-Zarr/COG clients.
* Secret storage.
* Credential exchange.
* Async streaming scheduler.
* LRU tile cache.
* Datoviz implementation changes.
* Remote renderer server implementation.
* Multi-resolution LOD optimization beyond a deterministic test policy.

## Consequences

This gives GSP a future-proof place for huge datasets without committing to a large distributed runtime. The reference proof validates the semantic model using a deterministic fake provider. Real cloud/server-side fetch can later reuse the same protocol objects with stricter security and capability negotiation.

The cost is that v0.1 adds a new abstraction layer, so task scope must remain tight. The implementation must avoid becoming a generic plugin system.

## Open questions

* Should `TiledImageSource` live under `src/gsp/data_sources.py` or a more general `src/gsp/protocol/data_sources.py` path?
* Should tile coordinates use `(level, row, col)` or `(level, x, y)`? I recommend `(level, x, y)` with explicit documentation that `x` is column and `y` is row.
* Should v0.1 query return source scalar values for all image modes, or only RGBA/display values? I recommend display RGBA plus scalar only when the fake provider exposes scalar data.
* Should VisPy2 expose tiled data sources immediately, or should this remain a low-level GSP proof first? I recommend low-level proof first.

---

# 3. Minimal Protocol Models

The exact names can change, but the v0.1 shape should be close to this.

## Extension manifest

```python
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping, Sequence


class ExtensionKind(str, Enum):
    VISUAL_FAMILY = "visual-family"
    TRANSFORM = "transform"
    DATA_SOURCE = "data-source"
    FORMAT_DECODER = "format-decoder"
    QUERY_PAYLOAD = "query-payload"
    TRANSPORT = "transport"


class ExtensionSupportLevel(str, Enum):
    CORE = "core"
    REFERENCE = "reference"
    OPTIONAL = "optional"
    EXPERIMENTAL = "experimental"


@dataclass(frozen=True)
class ExtensionManifest:
    id: str
    version: str
    kind: ExtensionKind
    title: str
    support_level: ExtensionSupportLevel = ExtensionSupportLevel.EXPERIMENTAL

    # Names of capability flags or requirements this extension needs.
    requires: tuple[str, ...] = ()

    # Optional features it can use if present.
    optional: tuple[str, ...] = ()

    # A JSON-schema-like dict or lightweight protocol schema.
    schema: Mapping[str, Any] = field(default_factory=dict)

    # Known implementation identifiers, not dynamically loaded in v0.1.
    implementations: Mapping[str, str] = field(default_factory=dict)
    # Example:
    # {"matplotlib": "reference", "datoviz": "unsupported"}

    fallback_policy: str = "reject"
    diagnostics_policy: str = "explicit"

    # Query payload schema name or dict, if relevant.
    query_contract: Mapping[str, Any] | None = None
```

Rules:

```text
- `id` must be globally namespaced, e.g. `gsp.tiled-image`.
- `version` must be semantic version or a simple protocol version string.
- v0.1 does not load code from manifests.
- v0.1 manifests are used for validation, capability advertisement, diagnostics, and test fixtures.
```

---

## Data-source descriptor

```python
class DataSourceKind(str, Enum):
    EAGER_IMAGE = "eager-image"
    TILED_IMAGE = "tiled-image"
    VIRTUAL_IMAGE = "virtual-image"
    OPAQUE = "opaque"


class DataLocality(str, Enum):
    IN_MEMORY = "in-memory"
    LOCAL_FILE = "local-file"
    CLIENT_FETCH = "client-fetch"
    SERVER_FETCH = "server-fetch"
    REMOTE_HANDLE = "remote-handle"
    SYNTHETIC = "synthetic"


class CredentialPolicy(str, Enum):
    NONE = "none"
    PRECONFIGURED = "preconfigured"
    FORBIDDEN = "forbidden"


class MaterializationPolicy(str, Enum):
    FULL = "full"
    TILE = "tile"
    VIEWPORT_MOSAIC = "viewport-mosaic"
    UNSUPPORTED = "unsupported"


@dataclass(frozen=True)
class DataSourceDescriptor:
    id: str
    kind: DataSourceKind
    extension_id: str | None = None
    extension_version: str | None = None

    # Logical source domain.
    shape: tuple[int, ...] = ()
    dtype: str = "uint8"
    channels: int = 1

    # Coordinate system metadata.
    coordinate_system: str = "pixel"
    extent: tuple[float, float, float, float] | None = None
    origin: str = "upper"

    locality: DataLocality = DataLocality.IN_MEMORY
    credential_policy: CredentialPolicy = CredentialPolicy.NONE
    materialization_policy: MaterializationPolicy = MaterializationPolicy.FULL

    metadata: Mapping[str, Any] = field(default_factory=dict)
```

This is the core protocol object. It should not contain executable fetch functions or credentials.

---

## Tiled image source

```python
class TileEncoding(str, Enum):
    ARRAY = "array"
    PNG = "png"
    JPEG = "jpeg"
    RAW = "raw"


class TileAvailability(str, Enum):
    COMPLETE = "complete"
    PARTIAL = "partial"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class TiledImageSource(DataSourceDescriptor):
    kind: DataSourceKind = DataSourceKind.TILED_IMAGE
    extension_id: str = "gsp.tiled-image"
    extension_version: str = "0.1"

    # Full-resolution logical image shape.
    # Shape should be H, W, C or H, W.
    shape: tuple[int, ...] = ()

    tile_shape: tuple[int, int] = (256, 256)

    # Number of pyramid levels. Level 0 is highest resolution unless otherwise specified.
    levels: int = 1
    level_downsample: tuple[int, ...] = (1,)

    # Valid source dtype and channels.
    dtype: str = "uint8"
    channels: int = 4

    encoding: TileEncoding = TileEncoding.ARRAY
    availability: TileAvailability = TileAvailability.COMPLETE

    # v0.1 should be synthetic/in-memory only for actual execution.
    locality: DataLocality = DataLocality.SYNTHETIC
    credential_policy: CredentialPolicy = CredentialPolicy.NONE
    materialization_policy: MaterializationPolicy = MaterializationPolicy.VIEWPORT_MOSAIC

    # Optional policy fields.
    max_tiles_per_request: int = 256
    missing_tile_policy: str = "transparent"
```

If Python dataclass inheritance is inconvenient because of frozen defaults, split this into composition:

```python
@dataclass(frozen=True)
class TiledImageSource:
    descriptor: DataSourceDescriptor
    tile_shape: tuple[int, int]
    levels: int
    ...
```

The protocol decision matters more than the Python inheritance form.

---

## Tile request/result

```python
@dataclass(frozen=True)
class TileIndex:
    level: int
    x: int  # tile column
    y: int  # tile row


@dataclass(frozen=True)
class TileRequest:
    source_id: str
    tile: TileIndex

    # Optional viewport-driven clipping in source pixel coordinates.
    source_rect: tuple[int, int, int, int] | None = None
    # x0, y0, width, height

    requested_dtype: str | None = None
    requested_channels: int | None = None


class TileStatus(str, Enum):
    OK = "ok"
    MISSING = "missing"
    UNSUPPORTED = "unsupported"
    FAILED = "failed"


@dataclass(frozen=True)
class TileResult:
    source_id: str
    tile: TileIndex
    status: TileStatus

    # Local in-process path: direct array-like object.
    data: Any | None = None

    # Shape/dtype metadata for validation.
    shape: tuple[int, ...] = ()
    dtype: str = ""

    # Source pixel bounds covered by this tile at its level.
    source_rect: tuple[int, int, int, int] | None = None

    diagnostic: str | None = None
```

For v0.1, `data` can be a NumPy array. Do not serialize it.

---

## Viewport mosaic request/result

The renderer proof should not manually fetch every tile in arbitrary ways. Define a deterministic helper model.

```python
@dataclass(frozen=True)
class ViewportTileRequest:
    source_id: str
    level: int
    # Source pixel rectangle requested for current viewport.
    source_rect: tuple[int, int, int, int]
    # Optional output mosaic size for reference rendering.
    output_shape: tuple[int, int] | None = None


@dataclass(frozen=True)
class ViewportMosaicResult:
    source_id: str
    level: int
    source_rect: tuple[int, int, int, int]
    data: Any
    tile_indices: tuple[TileIndex, ...]
    diagnostic: str | None = None
```

The reference Matplotlib renderer can consume this.

---

## Query/readout for tiled image

Extend, do not replace, the current query result.

```python
@dataclass(frozen=True)
class TiledImageQueryPayload:
    source_id: str
    level: int
    tile_x: int
    tile_y: int
    texel_x: int
    texel_y: int

    # Full-resolution or level-local source coordinate.
    source_x: int
    source_y: int

    # Optional normalized coordinate.
    uv: tuple[float, float] | None = None

    value: tuple[float, ...] | float | None = None
```

The core `QueryResult` can carry this as:

```python
extension_payload_kind = "gsp.tiled-image.query"
extension_payload = TiledImageQueryPayload(...)
```

or, if you do not yet want payload generics, include `metadata` in the query result for v0.1.

Prefer typed payload if feasible.

---

# 4. Capability Surface

## Add or reuse these capability fields

If the current `CapabilitySnapshot` already has `extensions`, reuse it. Add only small fields if necessary.

Recommended fields:

```python
@dataclass(frozen=True)
class CapabilitySnapshot:
    # existing fields...
    extensions: tuple[str, ...] = ()
    query_modes: tuple[str, ...] = ()

    supports_extension_manifests: bool = False
    supports_virtual_data_sources: bool = False
    supports_tiled_image_sources: bool = False

    # Local/reference support only.
    supports_in_memory_data_source: bool = True
    supports_synthetic_data_source: bool = True
    supports_local_file_data_source: bool = False
    supports_client_fetch_data_source: bool = False
    supports_server_fetch_data_source: bool = False
    supports_remote_handle_data_source: bool = False

    max_tiles_per_request: int = 0
    max_mosaic_pixels: int = 0
```

For Matplotlib reference v0.1:

```text
supports_extension_manifests = true
supports_virtual_data_sources = true
supports_tiled_image_sources = true
supports_synthetic_data_source = true
supports_in_memory_data_source = true
supports_client_fetch_data_source = false
supports_server_fetch_data_source = false
supports_remote_handle_data_source = false
extensions includes "gsp.tiled-image@0.1"
```

For Datoviz v0.4 adapter right now:

```text
supports_extension_manifests = true or false depending on whether adapter validates manifests;
supports_tiled_image_sources = false unless explicitly implemented;
adaptation = reject or unsupported diagnostic for TiledImageSource.
```

## Extension naming

Use stable strings:

```text
gsp.tiled-image@0.1
gsp.virtual-data-source@0.1
gsp.query.tiled-image@0.1
```

## Unsupported behavior

If a visual references a `TiledImageSource` and backend lacks support:

```text
adaptation outcome: reject
diagnostic category: unsupported-capability
diagnostic subject: data-source
message: backend does not support gsp.tiled-image@0.1
```

Do not silently materialize the full image unless:

1. the source has `materialization_policy="full"`; and
2. full materialization is bounded by capability limits; and
3. the adaptation emits a diagnostic saying it simplified.

For v0.1, prefer reject over clever fallback.

---

# 5. Reference Matplotlib Proof

## Local fake provider

Implement a deterministic fake provider:

```python
class FakeTiledImageProvider:
    def __init__(self, source: TiledImageSource):
        ...

    def get_tile(self, request: TileRequest) -> TileResult:
        ...

    def get_viewport_mosaic(self, request: ViewportTileRequest) -> ViewportMosaicResult:
        ...
```

The fake provider should:

```text
- generate tiles from coordinates deterministically;
- require no network;
- require no credentials;
- optionally support 1–2 pyramid levels;
- return NumPy arrays directly;
- expose enough metadata for query tests.
```

Suggested synthetic tile value:

```python
rgba[..., 0] = tile_x % 256
rgba[..., 1] = tile_y % 256
rgba[..., 2] = level % 256
rgba[..., 3] = 255
```

or include a gradient so texel-local query can be validated:

```python
rgba[..., 0] = source_x % 256
rgba[..., 1] = source_y % 256
rgba[..., 2] = level
rgba[..., 3] = 255
```

## Renderer behavior

Matplotlib reference renderer should materialize a **viewport mosaic**, not just one tile.

For v0.1:

```text
- Choose a fixed level from the source or request.
- Compute tile indices intersecting the image extent/viewport.
- Ask provider for needed tiles.
- Assemble a mosaic NumPy array.
- Render as ordinary image visual using existing image path.
```

If viewport-to-source mapping is not yet available, the proof can use the image visual extent and a requested source rectangle covering a deterministic test window.

## Query tests

The query proof should show:

```text
- query inside the tiled image returns hit;
- query outside returns miss or outside-panel according to existing semantics;
- returned payload includes source id;
- returned payload includes level/tile_x/tile_y;
- returned payload includes texel/source coordinate;
- displayed RGBA matches fake tile content;
- query does not require network or JSON/base64.
```

## Deferred/mocked

Keep deferred:

```text
- async tile loading;
- cache eviction;
- progressive refinement;
- server-side fetch;
- remote renderer ownership;
- missing tile retry;
- real LOD selection;
- Datoviz renderer support;
- security credentials.
```

---

# 6. Task List For Codex Agents

Recommended execution order.

## EXT-ADR-001 — Finalize extension/data-source ADR

Likely paths:

```text
adr/ADR-0004-extensions-virtual-data-sources-v01.md
spec/extensions.md
spec/data_sources.md
```

Goal:

```text
Convert this consultation answer into an accepted/proposed ADR and update specs.
```

Stop conditions:

```text
- v0.1 scope expands beyond static manifests and local fake tiled source;
- security policy becomes unclear;
- task tries to add a plugin loader.
```

---

## EXT-MODEL-001 — Add minimal extension and data-source protocol models

Likely paths:

```text
src/gsp/
src/gsp/protocol/
tests/
spec/extensions.md
spec/data_sources.md
```

Goal:

```text
Add dataclasses/enums for ExtensionManifest, DataSourceDescriptor, TiledImageSource, TileRequest, TileResult, locality/security/materialization enums.
```

Acceptance:

```text
- type/model tests pass;
- no network dependency;
- no JSON/base64 required;
- no plugin loading.
```

Stop conditions:

```text
- implementation requires broad resource-model redesign;
- conflicts with existing ImageVisual API.
```

---

## EXT-CAPS-001 — Add virtual data-source capabilities

Likely paths:

```text
src/gsp/
tests/
spec/capabilities.md
```

Goal:

```text
Extend or reuse CapabilitySnapshot fields for extension manifests and virtual/tiled data-source support.
```

Acceptance:

```text
- Matplotlib reference caps advertise gsp.tiled-image@0.1 support;
- unsupported backend can reject explicitly;
- tests cover support/reject behavior.
```

Stop conditions:

```text
- capability model needs high-level redesign.
```

---

## EXT-FAKE-001 — Implement fake tiled image provider

Likely paths:

```text
src/gsp/
tests/
fixtures/
```

Goal:

```text
Add deterministic in-memory fake tiled image provider and tests for tile requests/results.
```

Acceptance:

```text
- tile output deterministic;
- no network;
- no credentials;
- NumPy arrays returned directly;
- tests verify tile coordinates and data values.
```

Stop conditions:

```text
- provider becomes a general plugin registry.
```

---

## EXT-MPL-001 — Matplotlib viewport mosaic proof

Likely paths:

```text
src/gsp_matplotlib/
tests/
fixtures/
```

Goal:

```text
Make Matplotlib reference path render a TiledImageSource by materializing a deterministic viewport mosaic.
```

Acceptance:

```text
- test renders tiled image mosaic;
- existing eager ImageVisual tests still pass;
- unsupported behavior remains explicit where source unsupported.
```

Stop conditions:

```text
- rendering path would require broad ImageVisual redesign;
- implementation wants real LOD/network/cache logic.
```

---

## EXT-QUERY-001 — Query proof for tiled image

Likely paths:

```text
src/gsp/
src/gsp_matplotlib/
tests/
spec/query.md
```

Goal:

```text
Extend reference query for tiled images enough to return tile/source coordinate metadata.
```

Acceptance:

```text
- query hit returns source id, level, tile_x, tile_y, texel/source coordinate, displayed RGBA;
- miss/outside semantics match existing query model;
- no Datoviz dependency.
```

Stop conditions:

```text
- query result schema needs incompatible redesign;
- conflicts with M005 query semantics.
```

---

## EXT-VISPY2-001 — Optional VisPy2 exposure

Likely paths:

```text
src/vispy2/
tests/
examples/
spec/vispy2/api.md
```

Goal:

```text
Only after the low-level GSP proof, optionally expose a small VisPy2 helper for fake tiled images.
```

Acceptance:

```text
- explicitly experimental;
- emits GSP data-source objects;
- no real cloud/network API.
```

Stop conditions:

```text
- API starts to look like production cloud data API;
- extension model is not stable.
```

---

# 7. Non-Goals

Do not implement in M011/M012:

* dynamic plugin loading;
* Python package manager or entry-point discovery;
* arbitrary user code execution from manifests;
* cloud credential storage;
* real HTTP/S3/GCS/Zarr/OME-Zarr/COG/OpenStreetMap fetching;
* server-side fetch execution;
* remote renderer transport;
* async tile scheduler;
* background prefetch;
* cache eviction/LRU;
* progressive refinement;
* sophisticated LOD selection;
* Datoviz tiled image support;
* WebGPU tiled image support;
* production security model;
* user-facing VisPy2 cloud API;
* full image pyramid viewer;
* custom shader/visual extension system;
* generalized extension compatibility solver.

---

# 8. Risk Review

## Security and credential risks

The main risk is accidentally creating a protocol that encourages arbitrary URL fetch or secret embedding. Avoid this by:

```text
- no executable fetch callbacks in protocol objects;
- no credentials in manifests;
- no arbitrary URL fetching in reference implementation;
- `credential_policy="none"` for executable v0.1 proof;
- `preconfigured` only as metadata for future server-side deployments;
- no network tests.
```

## Scope risks

The biggest scope risk is turning “fake tiled source proof” into a full virtual data platform. Prevent this by:

```text
- one built-in source kind only;
- one fake provider only;
- Matplotlib reference only;
- no Datoviz requirement;
- no package/plugin loader;
- no async/cache/remote.
```

## Compatibility risks with Datoviz

Datoviz should not be required to support tiled virtual images now. The adapter can reject `gsp.tiled-image@0.1` explicitly. This preserves Datoviz as the flagship GPU backend without blocking extension architecture.

Later Datoviz support can map virtual/tiled images to sampled fields or streaming texture updates, but that is not v0.1.

## Compatibility risks with VisPy2

VisPy2 should not expose a polished cloud/tiled API before the GSP model stabilizes. If exposed at all, it should be experimental and local-only.

The initial proof should be GSP-level first.

## Protocol risks

Adding data sources introduces a second way to provide images: eager image data and virtual source references. Keep the boundary explicit:

```text
ImageVisual can use either:
- eager local image data; or
- data_source_ref to a compatible image-like source.
```

Do not duplicate all image styling in the data source. Image placement, interpolation, extent, origin, and query behavior remain visual/protocol semantics. The data source only describes data availability and materialization.

## Testing risks

Image/tile coordinate systems can easily drift. Tests must explicitly cover:

```text
- origin convention;
- tile x/y vs row/col;
- texel coordinate;
- displayed RGBA;
- source coordinate mapping;
- miss/outside-panel status.
```

This should be locked before any Datoviz or VisPy2 expansion.

