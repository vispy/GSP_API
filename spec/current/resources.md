# Resources and data

## Resource contract

A resource has validated identity, locality, mutability, usage, data type, shape, and payload rules. Backends must not infer a different shape or data interpretation from raw byte length alone.

| Rule | Requirement |
|---|---|
| `GSP-DATA-001` | Resource metadata is validated before any payload is read, copied, mapped, decoded, fetched, or uploaded. |
| `GSP-DATA-002` | The tuple `(dtype, shape, byte_order, strides/contiguity policy)` defines array interpretation; byte length alone never does. |
| `GSP-DATA-003` | A resource reference resolves by public resource ID and expected kind, never by a backend pointer or allocation handle. |

## Buffers

`BufferResource` represents ordinary finite data. The local path may carry NumPy arrays or `memoryview` values directly. JSON/base64 is permitted for fixtures, replay, debugging, and simple transport, but it is not mandatory protocol semantics.

### BufferResource

| Field | Type | Required | Default | Validation |
|---|---|---:|---|---|
| `id` | identifier | yes | — | Unique live resource ID. |
| `dtype` | registered scalar dtype | yes | — | Explicit width and signedness. |
| `shape` | non-empty tuple of non-negative integers | yes | — | Rank and dimensions are semantic. |
| `byte_length` | non-negative integer | yes | — | Must match payload view when present. |
| `usage` | non-empty set of usages | yes | — | Attribute, index, uniform, texture, or readback. |
| `mutability` | enum | no | `immutable` | `immutable`, `dynamic`, or `stream`. |
| `locality` | enum | no | `client-memory` | Client, server, or external. |
| `contiguous` | boolean | no | true | Core 0.2 accepts contiguous buffers only. |
| `data` | native byte view or null | locality-specific | null | In-process payload; exact `byte_length`. |
| `external_source` | source ID or null | locality-specific | null | Required for external locality. |

`GSP-DATA-004`: zero-length dimensions and zero-byte buffers are valid only where the consuming
record explicitly accepts an empty collection. Negative dimensions, dtype/length mismatch, and
non-contiguous core payloads are invalid.

`GSP-DATA-005`: immutable data cannot be updated. Dynamic updates replace an explicitly bounded
range atomically. Stream semantics require a negotiated stream capability and explicit ownership;
ordinary dynamic buffers do not imply producer/backend concurrent access.

## Texture2D

The accepted texture resource is immutable two-dimensional RGBA8 data with explicit width, height, and format. Textured meshes require:

- a declared `Texture2D` identifier;
- finite per-vertex UV coordinates shaped `(N, 2)`;
- UV topology matching mesh vertex indexing;
- the accepted visual-owned nearest-or-linear unlit sampling and color-combination rules.

Nearest and linear filtering are accepted for textured meshes. Repeat wrapping, mipmaps, color management, generated UVs, and separate UV indices remain outside the bounded contract.

### Texture2D

| Field | Type | Required | Default | Validation |
|---|---|---:|---|---|
| `id` | identifier | yes | — | Unique live resource ID. |
| `format` | texture format | no | `rgba8` | Only unmanaged RGBA8 is accepted in the bounded contract. |
| `width`, `height` | positive integers | derived or explicit | — | Must match payload shape. |
| `image` | contiguous `uint8[H,W,4]` | yes | — | No implicit RGB expansion or numeric scaling. |
| `origin` | texture-origin policy | no | contract-specific fixed value | Must match the material contract. |

`GSP-DATA-006`: protocol acceptance of `Texture2D` does not imply renderer support for any material.
The visual/material capability is negotiated independently.

## Data locality

Locality is explicit. A backend must not perform network, filesystem, decoder, or extension execution merely because a descriptor contains a URL or path. Security and credential policies are validated before materialization.

| Locality | Meaning |
|---|---|
| `client-memory` | Producer supplies native or transported bytes. |
| `server-memory` | Resource refers to bytes already owned by the session/server. |
| `external` | A negotiated data-source descriptor governs materialization. |

`GSP-DATA-007`: a URI is inert data until an accepted source kind, locality, credential policy,
decoder, size bound, and fetch policy authorize materialization. Diagnostic payloads redact secrets,
credential references, sensitive paths, and network-resolution details under the active security
profile.

## Virtual data sources

Data too large or dynamic for an ordinary buffer is represented by a data-source contract. Tiled and preconfigured sources expose bounded requests and availability states. Current HTTP-array work is limited and must not be described as general remote-data support.

### DataSourceDescriptor

| Field | Type | Required | Meaning |
|---|---|---:|---|
| `id` | identifier | yes | Descriptor identity. |
| `kind` | registered source kind | yes | Materialization/query contract. |
| `locality` | registered locality | yes | Where access occurs. |
| `source_ref` | opaque kind-specific reference | yes | Never executed directly. |
| `credential_policy` | registered policy | yes | Usually `none` in the accepted no-network profile. |
| `materialization_policy` | bounded policy | yes | Client/server/preconfigured behavior. |
| `limits` | typed limit record | yes | Bytes, tiles, pixels, requests, and time as applicable. |
| `metadata` | redacted string-keyed map | no | Non-authoritative metadata. |

`GSP-DATA-008`: every request is bounded before execution. A tile request declares source, index,
encoding, and requested region; a mosaic request declares maximum tile count and output pixels.
Unavailable data returns a typed availability state rather than malformed partial bytes.

`GSP-DATA-009`: decoders are separately identified and validated. The accepted `.npy` proof parses
the header under explicit dtype, rank, byte-order, and size limits before allocating or reading the
array payload. Object dtype and executable/pickled payloads are rejected.

## Resource revisions and snapshots

Immutable resources have revision zero. Dynamic resources increment a revision for every accepted
update. Frames and queries report or bind the resource revisions whose contents affected the
result.

`GSP-DATA-010`: ownership and copy behavior are transport/profile properties. Accepting a native
`memoryview` does not claim zero-copy; an implementation may copy while preserving semantics and
must document lifetime requirements for any borrowed view.
