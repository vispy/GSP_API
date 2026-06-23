# P007 - HTTP access and decoder architecture

Status: pending ChatGPT Pro response.

This needs ChatGPT Pro consultation.

## Why This Is Needed

S022 follows two completed safety stages:

- S020 completed remote data and dynamic extension security pre-design.
- S021 completed a no-network `preconfigured-source` resolver proof.

The next architectural question is narrower than "remote data": choose the first real remote access
direction and specify the protocol spine before implementation. The desired access mechanism is
HTTP, but HTTP must be modeled as an access/fetch mechanism, not as a source type. The first proof
does not need to be a tile pyramid. It may be a single HTTP-backed resource such as a JPEG/PNG
image/texture or a `.npy` typed array.

Do not implement HTTP fetch, URL parsing, credentials, decoders, network I/O, or dynamic loading
until the response is pasted or committed and converted into specs/ADRs/tasks.

This prompt is intentionally self-contained. Do not assume file attachments or repository access.

## Exact Prompt For ChatGPT Pro

```text
You are an architecture reviewer for GSP_API, a Python research prototype for a backend-independent
Graphics Server Protocol (GSP) for scientific visualization.

Your task is to decide and specify the first safe HTTP access/decoder architecture proof for S022.
This is a pre-implementation architecture review. Do not write implementation code. The answer must
be concrete enough for Codex worker agents to update specs, ADRs, fixtures, validation helpers, and
mission-sized task files without inventing protocol semantics.

The central framing is:

- HTTP is the desired first real access mechanism.
- HTTP is not a source type.
- Tile pyramid was only an example source contract.
- The first proof may instead be an HTTP single-resource proof, such as JPEG/PNG image/texture or
  `.npy` typed array.
- The architecture must separate:
  1. access/fetch: HTTP, S3, GCS, local sandbox, in-memory;
  2. source contract: image, texture, array, tiled image, volume, point chunks;
  3. decoder: JPEG/PNG, `.npy`, Zarr chunk, custom binary;
  4. resolver policy: admin allowlist, opaque handles, limits, credentials;
  5. renderer adapter: image visual, texture resource, array resource, tiled source.
- Pluggability must be safe: user-specific fetchers/decoders are installed/configured out of band
  by trusted server/admin configuration. Protocol payloads must not contain executable code, import
  paths, callbacks, package installation instructions, dynamic plugins, shader source, or arbitrary
  decoder configuration.
- Scenes should refer only to stable names/handles such as `source_id`, `source_kind`, `format`,
  `decoder_id`, and resolver-owned policy.

## Project Principles

GSP should allow one semantic visualization description to target:

- fast local GPU rendering through Datoviz v0.4;
- reference/publication rendering through Matplotlib;
- remote renderers;
- future web/browser paths through Datoviz/WebGPU where available;
- extension/data-source systems for huge distributed datasets.

Non-negotiable principles:

1. GSP is a server/session protocol inspired by LSP, not merely a Python object graph.
2. Local desktop use must have a fast in-process path with no mandatory JSON/base64 serialization.
3. JSON/base64 is allowed for fixtures, debugging, replay, and simple transport only.
4. Capability discovery and explicit adaptation are mandatory.
5. Visual families are semantic contracts, not backend draw calls.
6. Query/readback is first-class and should use a unified panel-query model.
7. Extensions must be manifest-, version-, and capability-driven.
8. Huge datasets should be represented as virtual data sources, not ordinary buffers.
9. Datoviz v0.4 is the flagship GPU backend.
10. Matplotlib is the reference/conformance/publication backend.
11. VisPy2 is the high-level Python producer of GSP scenes.
12. High-reasoning design work should be captured in durable specs, ADRs, and task files.
13. Existing source code is implementation material, not protocol authority.

Current architecture:

- GSP is a client/server/session protocol.
- A server may be in-process local renderer, subprocess, remote renderer, browser/worker runtime, or
  cloud GPU service.
- Protocol semantics are independent from encoding.
- Transport classes include `inproc`, `binary-ipc`, `network`, and `debug-json`.
- The local desktop path must not require JSON/base64.
- Control plane includes scene commands, visual creation/update, transforms, queries,
  capabilities, diagnostics, and events.
- Data plane includes buffers, textures, tiles/chunks, external data-source handles, server-side
  fetch descriptors, cache, and LOD policies.
- Every backend exposes a `CapabilitySnapshot`; unsupported behavior must accept, simplify with
  diagnostic, deactivate with diagnostic, or reject with fatal diagnostic. Security-sensitive
  unsupported behavior must reject fatally.

Authority order in this project:

1. PROJECT_CHARTER.md
2. ARCHITECTURE.md
3. SPEC_INDEX.md
4. `spec/**`
5. accepted ADRs and `.agent/decisions/**`
6. LEGACY_MAP.md
7. existing source code

## Current Stage State

Current stage:

| Stage | Title | State | Progress |
|---|---|---|---|
| S022 | Remote source family selection and consultation | in_progress | 15% before this packet |

Recent completed stages:

| Stage | Result |
|---|---|
| S020 | Remote data and dynamic extension security pre-design completed. |
| S021 | No-network `preconfigured-source` resolver proof completed. |

Completed S022 mission before this consultation:

| Mission | Result |
|---|---|
| M058 | Recorded that HTTP is an access mechanism, not a source type; recommended an HTTP single-resource consultation before tile pyramids. |

Open question:

| ID | Summary | Requires ChatGPT Pro |
|---|---|---|
| Q060-FIRST-REMOTE-SOURCE-FAMILY | Choose and design the first real remote-source family before any production fetch implementation. | yes |

## Current Extension and Data-Source Model

GSP extensions may define:

- visual families;
- transforms;
- data sources;
- data formats/decoders;
- query/readout payloads;
- transports.

Every extension needs:

- id;
- semantic version;
- kind;
- schema;
- capability requirements;
- implementation declarations;
- fallback policy;
- diagnostics policy;
- query contract where applicable.

Current extension policy:

- The implemented extension model is static metadata, not dynamic plugin loading.
- Manifests are used only for validation, capability advertisement, diagnostics, fixtures, and query
  payload contracts.
- Manifests must not load code, discover packages, declare Python imports, execute user callbacks,
  inject backend draw calls, or load runtime shaders.
- Dynamic extension loading is deferred.
- Implementation declarations describe already-installed trusted server capabilities; they are not
  instructions for loading code.
- Unknown manifest fields reject unless they live under a documented non-executable `x-` namespace.

Current data-source policy:

- Huge datasets should be modeled as virtual data sources, not ordinary buffers.
- Data sources should declare logical shape, coordinate system, chunk/tile scheme, LODs, fetch
  locality, cache policy, credential policy, materialization policy, and query/readout behavior.
- Remote renderers should eventually be able to fetch data server-side when permitted.
- Current executable localities are only `synthetic`, `in-memory`, and optionally
  `preconfigured-source` handles backed by administrator/test configuration.
- Current reserved or future localities include `local-file-sandboxed`, `client-materialized`,
  `server-resolved-remote`, `direct-remote-fetch`, and `browser-origin-fetch`.
- `preconfigured-source` means the scene supplies only an opaque resolver-known handle. Unknown
  handles reject fatally. Admin/test configuration owns any underlying URL/path/bucket/credential.
- Current credential policies are `none` and `preconfigured`, but the S021 executable proof supports
  only `none`.
- `inline` credentials are always invalid.
- Credential refs, if ever enabled, must be opaque, resolver-, tenant-, and session-authorized
  selectors; they must not reveal account identity.
- Current safe cache modes are `none` and optionally `session-memory`.
- Shared/persistent cache requires future key isolation across tenant/session, resolver, source,
  credential identity/version marker, extension id/version, decoder version, LOD/chunk coordinates,
  materialization parameters, and content generation or digest.

## Existing Data-Source Code Shape

Current `DataSourceKind` values:

```python
class DataSourceKind(str, Enum):
    EAGER_IMAGE = "eager-image"
    TILED_IMAGE = "tiled-image"
    VIRTUAL_IMAGE = "virtual-image"
    OPAQUE = "opaque"
```

Current `DataLocality` values:

```python
class DataLocality(str, Enum):
    IN_MEMORY = "in-memory"
    PRECONFIGURED_SOURCE = "preconfigured-source"
    LOCAL_FILE_SANDBOXED = "local-file-sandboxed"
    CLIENT_MATERIALIZED = "client-materialized"
    SERVER_RESOLVED_REMOTE = "server-resolved-remote"
    DIRECT_REMOTE_FETCH = "direct-remote-fetch"
    BROWSER_ORIGIN_FETCH = "browser-origin-fetch"
    LOCAL_FILE = "local-file"
    CLIENT_FETCH = "client-fetch"
    SERVER_FETCH = "server-fetch"
    REMOTE_HANDLE = "remote-handle"
    SYNTHETIC = "synthetic"
```

Current `CredentialPolicy` values:

```python
class CredentialPolicy(str, Enum):
    NONE = "none"
    PRECONFIGURED = "preconfigured"
    PRECONFIGURED_REF = "preconfigured-ref"
    DELEGATED = "delegated"
    INLINE = "inline"
    FORBIDDEN = "forbidden"
```

Current core `DataSourceDescriptor` shape:

```python
@dataclass(frozen=True, slots=True)
class DataSourceDescriptor:
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
    source_ref: dict[str, str] | None = None
    fetch_descriptor: dict[str, Any] | None = None
    credential_ref: str | None = None
    cache_policy: dict[str, Any] | None = None
    materialization_policy: MaterializationPolicy = MaterializationPolicy.FULL
    metadata: dict[str, Any] | None = None
```

Current implemented local tiled image proof:

- `TiledImageSource` has `shape`, `tile_shape`, `levels`, `level_downsample`, `dtype`, `channels`,
  `extent`, `origin`, `encoding`, `availability`, `locality`, `credential_policy`,
  `materialization_policy`, and `max_tiles_per_request`.
- Executable v0.1 tiled images require `credential_policy="none"`.
- Executable v0.1 tiled images support only `synthetic` and `in-memory` locality.
- The local proof has a deterministic `FakeTiledImageProvider` and Matplotlib reference rendering.
- Query/readback returns typed `TiledImageQueryPayload` fields such as source id, level, tile x/y,
  source x/y, texel x/y, uv, and value.

Current no-network preconfigured resolver proof:

- `NoNetworkPreconfiguredSourceResolver` maps opaque `resolver_id + source_id` handles to
  pre-registered synthetic or in-memory tiled sources.
- It never performs network I/O, path access, host resolution, credential lookup, or dynamic
  extension loading.
- The public proof handle is:
  - `resolver_id = "gsp.test.synthetic-resolver"`
  - `source_id = "public-demo-pyramid"`
- Capability record shape:

```json
{
  "resolver_id": "gsp.test.synthetic-resolver",
  "source_kinds": ["tiled-image"],
  "credential_policies": ["none"],
  "network_io": false,
  "source_ids": ["public-demo-pyramid"]
}
```

## S020 Security Decision

ADR-0008 accepted the following security posture:

- S020 defines protocol boundaries, validation rules, diagnostics, and conformance before any
  production remote fetch or dynamic extension execution is implemented.
- Executable data-source localities are limited to `synthetic`, `in-memory`, and optional
  `preconfigured-source`.
- Client-supplied direct fetch descriptors, arbitrary URLs, local paths, object-store URIs, signed
  URLs, request headers, cookies, and inline credentials are reserved or invalid and rejected by
  default.
- Dynamic extension loading is deferred.
- Extension manifests remain data-only protocol metadata. They must not import Python packages,
  declare entry points, execute hooks, load shaders, load decoders, or inject backend draw calls.
- Credential policy is limited to `none` and `preconfigured`. `preconfigured` means credentials, if
  any, are owned by the server/resolver administrator.
- Scenes, manifests, fixtures, replay logs, diagnostics, and debug JSON must never contain raw
  secrets or resolver outputs.
- Security-sensitive unsupported behavior must reject fatally.
- Debug/replay serialization must redact or reject secrets and private source details.

S020 hard stops:

- client-supplied arbitrary URLs;
- raw secrets or signed URLs in protocol payloads, fixtures, logs, or replay artifacts;
- dynamic Python imports, package entry points, callbacks, custom decoders, runtime shaders, or
  transform hooks;
- ambient cloud credentials or default SDK credential chains;
- inability to enforce source/host allowlists and private-address rejection;
- unbounded materialization, decompression, retry, redirect, concurrency, query, or cache behavior;
- cache keys that cannot isolate tenant/session, credential, source, resolver, extension version,
  and content generation;
- query/readback that cannot be scoped to declared source bounds and query contracts;
- debug/replay output that cannot reliably redact sensitive source and credential details.

## Current Security Validation and Diagnostics

Current no-network validation rejects:

- unsupported source locality;
- unknown preconfigured source handle;
- any `fetch_descriptor`;
- unsupported credential policy;
- any `credential_ref`;
- URL-like metadata;
- path-like metadata;
- sensitive keys;
- manifest fields that imply executable behavior.

Stable S020 diagnostic codes include:

- `GSP_SOURCE_LOCALITY_UNSUPPORTED`
- `GSP_SOURCE_HANDLE_UNKNOWN`
- `GSP_REMOTE_FETCH_DISABLED`
- `GSP_SERVER_SIDE_FETCH_DISABLED`
- `GSP_FETCH_DESCRIPTOR_REJECTED`
- `GSP_URL_SCHEME_FORBIDDEN`
- `GSP_URL_USERINFO_FORBIDDEN`
- `GSP_URL_HOST_NOT_ALLOWED`
- `GSP_URL_RESOLVES_PRIVATE`
- `GSP_URL_REDIRECT_REJECTED`
- `GSP_LOCAL_PATH_FORBIDDEN`
- `GSP_LOCAL_PATH_TRAVERSAL`
- `GSP_CREDENTIAL_POLICY_UNSUPPORTED`
- `GSP_CREDENTIAL_REF_REJECTED`
- `GSP_INLINE_SECRET_REJECTED`
- `GSP_MANIFEST_SCHEMA_INVALID`
- `GSP_MANIFEST_EXECUTION_FORBIDDEN`
- `GSP_EXTENSION_DYNAMIC_LOADING_DISABLED`
- `GSP_DECODER_PLUGIN_DISABLED`
- `GSP_SHADER_EXTENSION_DISABLED`
- `GSP_CHUNK_METADATA_INVALID`
- `GSP_CHUNK_LIMIT_EXCEEDED`
- `GSP_DECOMPRESSION_LIMIT_EXCEEDED`
- `GSP_CACHE_POLICY_UNSUPPORTED`
- `GSP_QUERY_SCOPE_VIOLATION`
- `GSP_QUERY_RESULT_LIMIT_EXCEEDED`
- `GSP_REPLAY_REDACTION_REQUIRED`

Current redaction placeholders:

- `<redacted:credential-ref>`
- `<redacted:source-ref>`
- `<redacted:url>`
- `<redacted:path>`
- `<redacted:secret>`

Current conservative capability metadata:

```json
{
  "data_sources": {
    "supported_source_localities": ["synthetic", "in-memory", "preconfigured-source"],
    "supported_credential_policies": ["none", "preconfigured"],
    "preconfigured_resolvers": [],
    "remote_fetch_descriptors": {"accepted": false},
    "supports_server_side_fetch": {"accepted": false},
    "cache_modes": ["none", "session-memory"]
  },
  "extensions": {
    "static_manifest_validation": true,
    "dynamic_discovery": false,
    "package_entry_points": false,
    "executable_hooks": false,
    "custom_decoders": false,
    "runtime_shaders": false
  },
  "security": {
    "redaction_profile": "gsp.s020.no-network",
    "diagnostic_redaction": true,
    "fixture_remote_sources_allowed": false
  }
}
```

## Existing S020 and S021 Fixtures

S020 has a no-network security-negative fixture package. It asserts:

- `direct-remote-fetch` with URL metadata rejects with source-locality, fetch-descriptor, remote
  fetch, and private-address diagnostics.
- Unknown `preconfigured-source` handles reject.
- Inline secrets, credential refs, and local paths reject.
- Executable manifest fields such as Python imports and runtime shader directives reject.
- Redaction replaces credential refs, URLs, paths, and authorization-like fields.
- Conservative capabilities advertise remote fetch and server-side fetch disabled.

S021 has a no-network preconfigured-source fixture package. It asserts:

- Known resolver handle materializes deterministic local tile data.
- Unknown handle rejects.
- `fetch_descriptor` on a preconfigured-source rejects.
- Fixture protocol has `network_io_allowed=false` and `dynamic_loading_allowed=false`.

## S022 Starting Architecture Note

S022 starts from a narrower decision than "implement remote data": use HTTP as the first real access
mechanism to test the architecture. HTTP is not itself the source type.

The first HTTP proof does not need to be a tile pyramid. Candidate first proofs:

- administrator-configured HTTP URL for a JPEG/PNG texture or image;
- administrator-configured HTTP URL for a `.npy` typed array;
- deterministic mock of either shape before production network I/O.

Required layer separation:

| Layer | Responsibility | Examples |
|---|---|---|
| Access/fetch | How bytes are obtained | HTTP, S3, GCS, local sandbox, in-memory |
| Source contract | What logical data is represented | image, texture, array, tiled image, volume, point chunks |
| Decoder | How bytes become typed data | JPEG/PNG, `.npy`, Zarr chunk, custom binary |
| Resolver policy | Who is allowed to fetch/decode what | admin allowlist, opaque handles, limits, credentials |
| Renderer adapter | How typed data becomes visuals/resources | image visual, texture resource, array resource, tiled source |

Safe pluggability model:

- Fetchers and decoders are installed/configured out of band by the server/resolver administrator.
- Capability snapshots advertise supported access schemes, source contracts, and decoder IDs.
- Scenes refer to `source_id`, `source_kind`, `format`, or `decoder_id` names that the resolver
  already knows.
- Manifests describe static contracts and requirements, not executable implementation loading.
- Resolver policy binds source handles to allowed access mechanism, decoder, resource limits,
  credential policy, cache policy, and diagnostics.

Recommended consultation target:

- HTTP single-resource proof before tile pyramids.
- Opaque handle examples:
  - `source_id="demo-http-jpeg-texture"`
  - `source_id="demo-http-npy-array"`
- Resolver-owned URL, never client-supplied.
- Bounded HTTP fetcher, initially mock/no-network if possible.
- Built-in decoder, for example JPEG/PNG or `.npy`.
- Output as image/texture resource or typed array resource.
- Conformance fixture covering capability advertisement, successful decode, rejection, redaction,
  and cache-key shape.

## Questions To Answer

Please decide and specify:

1. Whether HTTP single-resource is the right first architecture test before tile pyramids, Zarr,
   OME-Zarr, COG, map tiles, or point-cloud chunks. If not, explain the smallest better first test.
2. Whether JPEG/PNG image/texture or `.npy` typed array is the better first proof target. Consider:
   - protocol generality;
   - decoder/security risk;
   - dependency footprint;
   - capability expression;
   - renderer adapter usefulness;
   - conformance fixture simplicity;
   - future migration to tiled/Zarr/OME-Zarr.
3. A safe protocol model that separately names:
   - access mechanism;
   - source contract;
   - decoder;
   - resolver policy;
   - cache policy;
   - capabilities;
   - diagnostics;
   - renderer adapter/materialization target.
4. A pluggable decoder/fetcher model that supports user-specific trusted server-side configuration
   without protocol-level executable payloads, package installation instructions, import paths,
   callbacks, dynamic plugins, or manifest-declared decoder code.
5. Exact descriptor fields for the first proof. Include field names, value examples, allowed values,
   forbidden fields, and whether each field lives in scene payload, resolver config, capability
   metadata, diagnostic output, or debug/replay fixtures.
6. Exact capability fields for the first proof. Include access mechanisms, source contracts,
   decoder IDs/formats, credential policies, cache modes, byte limits, redirect policy, host policy,
   timeout/retry limits, decompression/decoded-size limits, and diagnostic redaction posture.
7. Validation and rejection rules for:
   - SSRF;
   - URL parsing;
   - scheme allowlist;
   - host allowlist;
   - loopback/private/link-local/metadata IPs;
   - DNS rebinding;
   - redirects;
   - URL userinfo;
   - fragments;
   - query-string secrets;
   - request headers and cookies;
   - content type;
   - content length;
   - byte limits;
   - decompression or decoder expansion;
   - `.npy` dtype/shape/header validation if `.npy` is selected;
   - JPEG/PNG dimensions/channel/color-mode validation if image is selected;
   - cache poisoning;
   - credential handling;
   - diagnostic/replay redaction.
8. Fixture and conformance strategy, preferably starting with no-network/mock fetch before real
   network I/O. Specify positive, negative, redaction, capability, cache-key, and eventual live
   network smoke fixtures.
9. Stop conditions requiring another design review before implementation can continue.
10. A staged implementation plan with mission-sized tasks. Include which tasks are spec/ADR only,
    which are no-network/mock validation, which may introduce real HTTP I/O, and what must be true
    before each transition.

## Constraints For Your Answer

- Do not propose client-supplied arbitrary URLs for the first proof.
- Do not put raw URLs, signed URLs, secrets, auth headers, cookies, local paths, internal hostnames,
  resolver outputs, DNS results, or cache internals in scenes, manifests, fixtures, logs, diagnostics,
  or debug JSON.
- Do not rely on dynamic Python imports, package entry points, package installation, callbacks,
  executable manifests, runtime shader loading, or protocol-level decoder plugins.
- Do not require Datoviz implementation as a prerequisite.
- Preserve Matplotlib as the reference/conformance backend.
- Preserve the local in-process fast path without mandatory JSON/base64.
- Keep HTTP as an access mechanism and keep source contract/decoder/renderer adapter separate.
- Prefer no-network/mock fetch before production network I/O.
- Security-sensitive unsupported behavior must reject fatally, not simplify or silently deactivate.
- The first proof should be small enough for bounded Codex worker missions.

## Expected Output Format

Please respond in exactly these sections:

1. Executive Decision
   - State whether HTTP single-resource should be first.
   - State whether the first proof target should be JPEG/PNG image/texture, `.npy` typed array, or
     another explicitly scoped target.
   - Include a short rationale and key tradeoffs.

2. Layered Protocol Model
   - Provide a table with columns: Layer, Protocol Name/Field, Resolver/Admin Config, Capability
     Field, Renderer Adapter, Notes.

3. First-Proof Descriptor Schema
   - Provide a concrete schema/table for the scene-visible descriptor fields.
   - Provide a separate schema/table for resolver/admin-only configuration fields.
   - Mark forbidden protocol fields explicitly.
   - Include at least one positive descriptor example and at least three rejected descriptor
     examples.

4. Capability Schema
   - Provide exact capability field names and example values.
   - Distinguish public capability metadata from private resolver configuration.

5. Decoder and Fetcher Pluggability Model
   - Specify how trusted server/admin installed fetchers and decoders are identified.
   - Specify what scenes/manifests may reference.
   - Specify what scenes/manifests must never contain.
   - Specify how user-specific but trusted configuration is authorized without executable payloads.

6. Validation and Rejection Rules
   - Provide deterministic rules and diagnostic codes for URL/SSRF, redirect, credential,
     content-type, byte/decode limits, cache, redaction, and decoder-specific validation.
   - Reuse existing diagnostic codes when appropriate and propose new codes only when needed.

7. Cache and Integrity Policy
   - Specify first-proof cache modes.
   - Specify cache-key isolation fields.
   - Specify poisoning prevention and digest/content-generation rules.
   - Specify what must be omitted or redacted from debug/replay output.

8. Fixture and Conformance Strategy
   - Specify no-network/mock fixture shape first.
   - Specify positive and negative cases.
   - Specify capability and redaction fixtures.
   - Specify the gate for optional real network smoke tests.

9. Stop Conditions
   - List concrete conditions that require another design review.

10. Staged Implementation Plan
    - Provide mission-sized tasks with titles, scope, deliverables, validation, and stop conditions.
    - Clearly mark implementation paused until this response is committed/pasted and reviewed.
```
