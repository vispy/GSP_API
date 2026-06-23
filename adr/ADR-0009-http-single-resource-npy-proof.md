# ADR-0009 - HTTP single-resource `.npy` proof

## Status

Accepted

## Context

S020 accepted a security-first posture for remote data and dynamic extensions. It reserved remote
descriptor vocabulary, rejected arbitrary client-supplied fetch by default, deferred dynamic loading,
and required redaction and negative conformance before runtime remote data work.

S021 proved that GSP can resolve opaque `preconfigured-source` handles without network I/O. That
proof maps administrator/test handles to deterministic local tiled sources and preserves the rule
that scenes never serialize underlying locations or secrets.

S022 needed to choose the first real remote access direction. The user wants HTTP first, but HTTP is
an access mechanism, not a source type. Tile pyramid was only an example and should not force the
first proof into tile, LOD, cache, or distributed chunk semantics.

This decision follows ChatGPT Pro consultation `P007`, recorded in
`.agent/consultations/P007-response.md`.

## Decision

The first S022 architecture test is an HTTP single-resource proof, not a tile pyramid, Zarr,
OME-Zarr, COG, map tile, point-cloud chunk, or JPEG/PNG image proof.

The first source contract is a bounded typed array decoded from `.npy` bytes:

```text
preconfigured opaque source handle
-> resolver-owned mock HTTP byte access
-> built-in gsp.decoder.npy.v1 policy
-> bounded array resource materialization
-> optional Matplotlib reference rendering/query for rank-2 arrays
```

HTTP remains an access/fetch mechanism. Scenes and fixtures must not use `source_kind="http"`.
The protocol model separates:

- access/fetch: HTTP, later S3/GCS/local sandbox/in-memory;
- source contract: first `array`, later image, texture, tiled image, volume, point chunks;
- decoder: first `gsp.decoder.npy.v1`, later JPEG/PNG, Zarr chunk, or custom binary only after
  review;
- resolver policy: administrator allowlist, opaque handles, byte/decode limits, credentials, cache,
  and diagnostics;
- renderer adapter: first `array-resource`, later texture resource, image visual, tiled source, or
  backend-specific upload.

The first proof remains no-network/mock. It may advertise an HTTP access mechanism using
`gsp.fetcher.http.mock.v1`, but it must not perform network I/O. Real HTTP I/O requires a later
design gate after mock conformance, redaction, cache isolation, SSRF policy, redirect rejection, TLS,
timeout, byte-limit, and diagnostic tests exist.

The first proof uses `credential_policy="none"`. Credential references, signed URLs, headers,
cookies, bearer tokens, ambient cloud credentials, and inline secrets remain invalid.

Fetchers and decoders are trusted server capabilities. They may be installed or configured out of
band by a server or resolver administrator. Protocol payloads and manifests must not contain Python
import paths, package installation instructions, callbacks, executable hooks, dynamic plugin
identifiers, decoder source code, arbitrary decoder configuration, runtime shaders, raw URLs, local
paths, DNS results, cache keys, or resolver private configuration.

No Datoviz implementation requirement is introduced by this ADR.

## In Scope

- ADR/spec baseline for the HTTP single-resource `.npy` array proof.
- Descriptor fields for source contract, format, decoder id, opaque source handle, cache mode, and
  materialization target.
- Public capability fields for configured-only HTTP access, mock fetcher identity, `.npy` decoder
  policy, byte/decode limits, credential policy, cache modes, and redaction posture.
- Private resolver/admin configuration vocabulary for future implementation, kept out of protocol
  artifacts.
- Diagnostic codes and rejection policy for source contract, decoder, content type/encoding, URL
  details, HTTP status, TLS, timeout, and DNS rebinding.
- No-network/mock conformance strategy for success, rejection, redaction, cache isolation, and
  optional Matplotlib reference materialization/query.

## Out of Scope

- Real HTTP network I/O.
- URL parsing, DNS resolution, TLS validation, redirect handling, connection pooling, retries, or
  sockets in this stage.
- Credentials or credential references.
- Client-supplied URLs, object-store URIs, local paths, signed URLs, request headers, cookies, or
  fetch descriptors.
- JPEG/PNG image decoding, Zarr/OME-Zarr, tile pyramids, COG, map tiles, volumes, point chunks, or
  custom binary formats.
- Dynamic decoder plugins, Python imports, package entry points, package installation, callbacks,
  runtime shaders, executable manifests, or backend draw-call injection.
- Persistent/shared/cross-session cache.
- Datoviz remote data support.

## Stop Conditions

Implementation must stop for another design review if a planned feature requires any of the
following:

- client-supplied arbitrary URLs, signed URLs, object-store URIs, or fetch descriptors;
- credential policy beyond `none` for the first HTTP proof;
- auth headers, cookies, bearer tokens, API keys, signed query strings, or ambient credentials;
- redirect following;
- plain live `http` instead of HTTPS-only live access;
- private network, loopback, link-local, metadata-service, intranet, local-file, or wildcard host
  access;
- inability to enforce DNS rebinding protection, TLS validation, byte/time limits, or redaction;
- persistent, shared, cross-session, or cross-tenant cache;
- diagnostics/replay that expose cache keys, DNS results, raw URLs, response headers, response
  bodies, digests, or resolver internals;
- JPEG/PNG, compressed arrays, Zarr, OME-Zarr, COG, tile pyramids, map tiles, volume chunks, or
  point-cloud chunks;
- dynamic decoder plugins, imports, package entry points, callbacks, runtime shaders, or executable
  manifests;
- `.npy` object dtype, structured dtype, string dtype, pickle, Fortran-order arrays, unknown shape,
  unbounded dtype/rank, or unbounded allocation;
- automatic retry behavior beyond zero retries;
- HTTP content encodings other than identity;
- query/readback that cannot be bounded by declared array shape and result limits;
- security-sensitive unsupported behavior that would be simplified or silently deactivated instead
  of fatally rejected;
- real network I/O before no-network/mock conformance and redaction pass.

## Consequences

S022 can now proceed with bounded no-network/mock design and validation work. The first
implementation missions should define the protocol schema, conservative capabilities, diagnostic
codes, a mock configured HTTP access contract, and a safe `.npy` decoder policy without opening
sockets or parsing live URLs.

Later remote source families should reuse this access/decoder/resolver/capability spine. JPEG/PNG,
tile pyramids, Zarr/OME-Zarr, COG, map tiles, volumes, point chunks, credentials, and real HTTP I/O
each remain separately gated.
