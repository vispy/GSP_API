# P005 - Versioned conformance fixture schema and array transport

Status: pending ChatGPT Pro response.

## Why This Is Needed

S018 has a working Python/in-process conformance replay harness, an explicit backend matrix, and a
deterministic debug-json diagnostic report. The next question is whether and how to graduate from
diagnostic JSON to a versioned fixture schema with array/base64 transport.

This is architectural because it affects protocol compatibility, fixture stability, transport
boundaries, large-array handling, backend certification semantics, and future Datoviz conformance.
Do not implement a versioned schema or array/base64 transport until the Pro response is pasted or
committed.

This prompt is intentionally self-contained. Do not assume file attachments or repository access.

## Exact Prompt For ChatGPT Pro

```text
You are an architecture reviewer for the GSP / VisPy2 project.

GSP is a backend-independent Graphics Server Protocol for semantic scientific visualization. VisPy2
is the high-level Python producer API that targets GSP. Matplotlib is the
reference/conformance/publication backend. Datoviz v0.4-dev is the flagship GPU backend. GSP is
intended to be a server/session protocol, not merely a Python object graph.

Your task is to decide the architecture for a future versioned conformance fixture schema and
array/base64 transport. The answer must be concrete enough for Codex worker agents to update specs,
tasks, and tests without inventing semantics. Do not propose implementation code unless needed for
clarity.

## Current Project Principles

1. GSP is a server/session protocol inspired by LSP, not merely a Python object graph.
2. Local desktop use must have a fast in-process path with no mandatory JSON/base64 serialization.
3. JSON/base64 is allowed for fixtures, debugging, replay, and simple transport only.
4. Capability discovery and explicit adaptation are mandatory.
5. Visual families are semantic contracts, not backend draw calls.
6. Query/readback is first-class and uses a unified panel-query model.
7. Extensions are manifest-, version-, and capability-driven.
8. Huge datasets should be represented as virtual data sources, not ordinary buffers.
9. Datoviz v0.4-dev is the flagship GPU backend.
10. Matplotlib is the reference/conformance/publication backend.
11. Existing source code is implementation material, not protocol authority.

## Current Mission State

Current stage:

| Stage | Title | State | Progress |
|---|---|---|---|
| S018 | Conformance fixture and replay harness | in_progress | 70% |

Recently completed S018 missions:

| Mission | Title | Result |
|---|---|---|
| M036 | In-process conformance replay harness | Python/in-process replay over existing fixtures. |
| M037 | Backend conformance matrix | Matplotlib pass, Datoviz clean skip. |
| M038 | Debug-json conformance report | JSON-safe semantic report, non-authoritative. |
| M039 | Diagnostic conformance report hardening | Deterministic tool output, still non-authoritative. |
| M040 | Versioned fixture schema decision packet | This consultation packet; no schema implementation. |

Current Mission Control recommendation after this packet:

- Paste this packet into ChatGPT Pro and commit or paste the response before implementing a
  versioned fixture schema or array/base64 transport.
- Keep Datoviz live query identity payload investigation deferred until the v0.4 runtime can fill
  visual_family/item_id/texel/value fields.

## Current Transport Spec

Transport is not protocol semantics.

Required transport classes:

| Transport | Purpose |
|---|---|
| inproc | Local desktop fast path, direct objects/memoryviews/ctypes, no JSON/base64 |
| debug-json | Fixtures, replay, tests, simple demos |
| binary-ipc | Future shared memory or binary chunk transport |
| network | Remote renderer and server-side data fetch |

The local desktop path must not require JSON/base64 serialization.

## Current Resource / Data Source Facts

Resource kinds include buffer, texture, sampled field, virtual data source, parameter block, and
external/live resource handle.

The initial BufferResource model requires contiguous buffers. Strided views may be represented by
attribute stride metadata, but non-contiguous resource ownership is deferred.

Virtual data sources are not ordinary buffers. `TiledImageSource` describes logical source data and
tile materialization separately from eager `BufferResource` bytes. The local proof returns direct
NumPy arrays from tile and viewport mosaic helpers without mandatory serialization.

## Current Conformance Fixture State

Conformance fixtures define stable semantic behavior for the v0.1 reference path.

They are currently Python/in-process fixtures, not JSON fixtures. This is intentional: the local fast
path must carry protocol objects, NumPy arrays, and memoryviews directly without mandatory
JSON/base64 serialization.

Currently covered:

- stable protocol object IDs;
- reference `CapabilitySnapshot` for the v0.1 slice;
- point visual with float32 positions, rgba8 colors, and scalar-per-item sizes;
- image visual with rgba8 data, explicit extent, and explicit origin;
- point-over-image panel query with frontmost z-order behavior;
- Matplotlib reference rendering for point and image visuals;
- semantic x/y guide fixture with explicit x ticks, deterministic auto y ticks, labels, grid intent,
  and panel title;
- guide query fixture coverage for tick hits, misses, and unsupported provider status;
- local tiled-source fixture with static manifest linkage, clipped viewport mosaic materialization,
  Matplotlib reference rendering, and typed tiled-image query payload;
- in-process replay harness that returns semantic point/image, guide, and tiled-source results;
- backend conformance matrix with Matplotlib pass and Datoviz clean-skip expectations;
- minimal debug-json report over semantic replay results, with array transport omitted;
- deterministic `tools/conformance_debug_report.py` diagnostic report output.

Not covered yet:

- Datoviz rendering or query execution;
- Datoviz conformance pass requirements;
- VisPy2 producer API conformance fixtures;
- production transport encodings;
- JSON/base64 replay fixtures;
- versioned JSON schema authority;
- general data/guides/all-rendered query-scope precedence beyond existing tests.

## Current In-Process Replay Result Shape

The current replay result contains:

- `server_name: str`
- `visual_families: tuple[str, ...]`
- `extensions: tuple[str, ...]`
- `point_query: QueryResult`
- `guide_query: QueryResult`
- `guide_miss: QueryResult`
- `tiled_query: QueryResult`
- `tiled_mosaic_source_rect: tuple[int, int, int, int]`
- `tiled_mosaic_shape: tuple[int, ...]`

The replay intentionally does not serialize NumPy arrays. It verifies semantic behavior and array
shape/source-rectangle metadata.

## Current Backend Matrix

The backend conformance matrix records:

- `matplotlib`: `pass`, using the deterministic reference replay harness;
- `datoviz`: `skip`, with a diagnostic reason derived from active Python binding state.

The Datoviz entry is intentionally visible but skipped until a backend replay adapter can map stable
application visual IDs and define guide/tiled-source expectations.

## Current Debug JSON Report

The current deterministic debug report:

- is emitted by `tools/conformance_debug_report.py`;
- is sorted, indented, and newline-terminated;
- contains `report_kind="gsp.conformance.debug-json"`;
- contains `version="0.1"`;
- contains `schema_authority=false`;
- contains `array_transport="omitted"`;
- includes backend pass/skip outcomes;
- includes Matplotlib semantic replay query summaries;
- includes the Datoviz skip reason;
- omits NumPy arrays and memory buffers.

It is explicitly diagnostic. Consumers must not treat it as the versioned fixture schema or array
transport contract.

## Current Query Model

GSP uses a unified panel query:

```text
What rendered scene contribution is under this panel coordinate?
```

Key enums:

```python
class QueryCoordinateSpace(str, Enum):
    PANEL = "panel"
    DATA = "data"

class QueryScope(str, Enum):
    DATA = "data"
    GUIDES = "guides"
    ALL_RENDERED = "all-rendered"

class QueryHitPolicy(str, Enum):
    FRONTMOST = "frontmost"
    ALL = "all"

class QueryPayload(str, Enum):
    IDENTITY = "identity"
    COORDINATE = "coordinate"
    COLOR = "color"
    VALUE = "value"

class QueryStatus(str, Enum):
    HIT = "hit"
    MISS = "miss"
    OUTSIDE_PANEL = "outside-panel"
    UNSUPPORTED = "unsupported"
    STALE = "stale"
    DROPPED = "dropped"
    FAILED = "failed"

class VisualFamily(str, Enum):
    POINT = "point"
    IMAGE = "image"
```

`QueryResult` includes request id, status, hit boolean, panel coordinate, optional hit payload
fields, optional extension payload kind/value, and optional diagnostic. Non-hit results must not
include hit payload fields. Unsupported/stale/dropped/failed results require diagnostics.

Existing extension query payloads:

- guide query payload kind: `gsp.guide-query@0.1`;
- tiled image query payload kind: `gsp.tiled-image@0.1.query`.

## Current Extension / Tiled Source Facts

The static tiled-image extension is capability-driven. Current conformance coverage includes a
synthetic/local `TiledImageSource`, clipped viewport mosaic materialization, and typed tiled-image
query payloads.

Important constraint: huge datasets should not be serialized as ordinary JSON arrays. Future JSON
fixtures may need compact array chunks, base64-encoded bytes with dtype/shape/order metadata, file
references, or omitted array payloads depending on fixture purpose.

## Decision Needed

Please recommend a concrete architecture for the future versioned conformance fixture schema and
array/base64 transport.

Questions to answer:

1. Should GSP graduate the current diagnostic debug-json report into a versioned fixture schema, or
   create a separate `gsp.conformance.fixture` schema and keep debug-json separate?
2. What top-level schema sections should exist for fixtures: metadata, capabilities, scene objects,
   resources/arrays, queries, backend expectations, extension manifests, outputs?
3. How should arrays be represented for JSON fixtures?
   - inline nested JSON arrays;
   - base64 bytes with dtype/shape/order/checksum;
   - external file references;
   - omitted arrays with semantic summaries;
   - some combination by size/purpose.
4. What exact metadata should array chunks include: dtype, shape, byte_order, memory_order, encoding,
   compression, checksum, semantic role, resource id?
5. How should virtual/tiled data sources be represented without pretending huge data is an eager
   buffer?
6. How should extension query payloads be serialized while preserving extension boundaries?
7. How should backend expectations be represented so Matplotlib can pass, Datoviz can skip or fail
   with diagnostics, and future backends can certify partial support honestly?
8. What should the compatibility/versioning policy be for fixture schema versions and protocol
   versions?
9. What should be explicitly deferred from the first schema slice?
10. What implementation missions should follow, in order, with stop conditions?

## Constraints

- Do not require JSON/base64 for local in-process desktop use.
- Do not make debug-json diagnostic output a compatibility contract unless you explicitly recommend
  that and justify it.
- Do not require Datoviz conformance pass until GSP has stable Datoviz runtime query identity fields.
- Do not serialize large virtual datasets as ordinary eager arrays.
- Preserve extension boundaries and versioned payload kinds.
- Prefer a first schema slice that is small enough to implement and test in this repository.
- Matplotlib remains reference/conformance backend.
- Datoviz remains visible in the matrix, even if skipped.

## Expected Output Format

Please produce exactly this structure:

# Consultation Result: Versioned Conformance Fixture Schema

## Recommendation

State the recommended architecture in 5-10 bullets.

## Schema Shape

Provide a proposed top-level JSON object shape using concise pseudo-JSON. Include required and
optional sections.

## Array Transport

Specify the recommended first-slice array representation and what is deferred. Include required
metadata fields and size/encoding rules.

## Virtual Data Sources

Specify how tiled/virtual data sources should appear in fixtures without eager serialization.

## Query And Extension Payloads

Specify how query results and extension payloads should be serialized.

## Backend Expectations

Specify pass/skip/fail/xfail semantics and required diagnostics.

## Versioning Policy

Specify fixture schema versioning rules and relationship to GSP protocol versions.

## First Implementation Missions

List 3-6 missions with goal, acceptance criteria, and stop conditions.

## Explicit Deferrals

List what must not be implemented in the first slice.

## Decision Record Draft

Provide a short ADR-style draft decision suitable for committing after review.
```

## Blocked Decisions

- Whether debug-json remains permanently diagnostic or becomes a schema seed.
- First-slice array representation.
- Required metadata for array chunks.
- Fixture schema versioning policy.
- Backend expectation semantics beyond current pass/skip diagnostic matrix.
- How extension payloads appear in schema without collapsing extension boundaries.

## Expected Output Format

The expected output format is included in the prompt above. Paste the ChatGPT Pro response into
`.agent/consultations/P005-response.md` or commit it as an equivalent response artifact.
