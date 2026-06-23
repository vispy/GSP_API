# ADR-0008 - Remote data and dynamic extension security pre-design

## Status

Accepted

## Context

S017 introduced static extension manifests and a local virtual tiled-image source proof. The proof is
intentionally safe: `gsp.tiled-image@0.1` supports synthetic and in-memory data only, does not fetch
remote data, and does not load extension code from manifests.

The next protocol questions are higher risk. Remote data can expose server-side request forgery,
path traversal, credential leakage, cache poisoning, decompression bombs, resource exhaustion, and
query/readback exfiltration. Dynamic extension loading can introduce executable supply-chain risk.

This decision follows ChatGPT Pro consultation `P006`, recorded in
`.agent/consultations/P006-response.md`.

## Decision

S020 is a security pre-design stage. It defines protocol boundaries, validation rules, diagnostics,
and conformance requirements before any production remote fetch or dynamic extension execution is
implemented.

For v0.2 planning, executable data-source localities are limited to:

- `synthetic`;
- `in-memory`;
- optional `preconfigured-source` handles backed by administrator configuration or a no-network
  mock resolver.

Client-supplied direct fetch descriptors, arbitrary URLs, local paths, object-store URIs, signed
URLs, request headers, cookies, and inline credentials are reserved or invalid and must be rejected
by default.

Dynamic extension loading is deferred. Extension manifests remain data-only protocol metadata. They
must not import Python packages, declare entry points, execute hooks, load shaders, load decoders, or
inject backend draw calls.

Credential policy is limited to `none` and `preconfigured`. `preconfigured` means credentials, if
any, are owned by the server or resolver administrator. Scenes, manifests, fixtures, replay logs,
diagnostics, and debug JSON must never contain raw secrets or resolver outputs.

Security-sensitive unsupported behavior must reject fatally. Simplification and deactivation are
acceptable for visual fidelity gaps, but not for arbitrary fetch, credentials, path traversal,
dynamic code, resource-limit violations, cache isolation failures, or query-scope violations.

Debug/replay serialization must redact or reject secrets and private source details. Fixture and
diagnostic artifacts must not leak signed URLs, local paths, internal hostnames, private IPs,
credential references that reveal account identity, cache keys, or external restricted data.

No Datoviz implementation requirement is introduced by this ADR.

## In Scope

- Source descriptor fields for future remote-capable sources.
- Source locality, credential, cache, materialization, query/readback, and diagnostics policy.
- Capability fields that advertise dangerous features as absent by default.
- Static manifest trust model and prohibited dynamic extension behaviors.
- Redaction rules for debug/replay artifacts.
- Negative conformance requirements that validate rejection without network I/O.
- Optional no-network preconfigured resolver proof.

## Out of Scope

- Real HTTP, S3, GCS, Zarr, OME-Zarr, COG, map-tile, STAC, DVID, TileDB, or custom chunk clients.
- Client-supplied arbitrary URL fetching.
- Production server-side fetch.
- Browser/WebGPU fetch paths.
- OAuth, cloud IAM, token refresh, SDK credential chains, or secret storage.
- Signed URL support as a first-class protocol feature.
- Dynamic Python package discovery, entry points, package-manager integration, dependency solving,
  executable hooks, runtime shaders, custom decoders, or transform callbacks.
- Async prefetch, retry engines, persistent caches, or progressive refinement against real remote
  data.
- Multi-tenant production renderer implementation.

## Stop Conditions

Implementation must stop for another design review if a planned feature requires any of the
following:

- client-supplied arbitrary URLs;
- raw secrets or signed URLs in protocol payloads, fixtures, logs, or replay artifacts;
- dynamic Python imports, package entry points, callbacks, custom decoders, or runtime shaders;
- ambient cloud credentials or default SDK credential chains;
- inability to enforce source/host allowlists and private-address rejection;
- unbounded materialization, decompression, retry, redirect, concurrency, query, or cache behavior;
- cache keys that cannot isolate tenant/session, credential, source, resolver, extension version,
  and content generation;
- query/readback that cannot be scoped to declared source bounds and query contracts;
- debug/replay output that cannot reliably redact sensitive source and credential details.

## Consequences

The protocol can reserve vocabulary for future remote data without creating an accidental network
feature. Conformance can now grow negative validation fixtures before runtime fetch code exists.

The next safe implementation work is validation and fixtures: reject unsafe descriptors, prove
redaction, advertise conservative capabilities, and optionally add a no-network mock resolver for
preconfigured handles.
