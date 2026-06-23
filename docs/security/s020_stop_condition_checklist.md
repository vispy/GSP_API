# S020 stop-condition checklist

S020 completed the remote data and dynamic extension security pre-design. The next stage may build
only a no-network `preconfigured-source` resolver proof unless these checks are revisited.

## Completed S020 artifacts

- ChatGPT Pro consultation packet and response: `P006`.
- ADR-0008 remote data and dynamic extension security pre-design.
- Spec patches for data sources, extensions, capabilities, and conformance fixtures.
- No-network protocol validation helpers and stable security diagnostic codes.
- JSON security-negative conformance fixture records.
- User-facing remote data and extension security note.

## Allowed next work

- No-network resolver registry for administrator/test preconfigured source handles.
- Deterministic synthetic or in-memory tile/materialization responses.
- Capability advertisement for known resolver handles.
- Diagnostics for unknown handles, disabled fetch, unsafe credentials, and redaction failures.
- Fixture/replay integration for the resolver proof.

## Hard stops

Stop and request another design review if work requires any of the following:

- client-supplied arbitrary URLs, object-store URIs, or local paths;
- HTTP/S3/GCS/Zarr/OME-Zarr/COG/map-tile/STAC/DVID/TileDB production fetch;
- raw secrets, signed URLs, auth headers, cookies, API keys, or resolver outputs in protocol data;
- OAuth, cloud IAM, token refresh, browser login, SDK credential chains, or secret storage;
- dynamic Python imports, entry points, package discovery, dependency solving, callbacks, hooks,
  custom decoders, runtime shaders, or backend draw-call injection;
- host allowlist, redirect, DNS/private-address, timeout, retry, decompression, cache, or query
  enforcement that cannot be represented as deterministic validation;
- tenant/session/cache/credential/source isolation that cannot be expressed in cache keys;
- query/readback that cannot be scoped to declared source bounds and query contracts;
- debug-json, replay, fixture, or diagnostic output that cannot reliably redact sensitive details;
- Datoviz API changes as a prerequisite for the no-network resolver proof.

## S021 opening decision

Open S021 for a no-network `preconfigured-source` resolver proof. The first mission should implement
only deterministic local handles and fixture-backed validation. Real remote fetch and dynamic
extension execution remain out of scope.
