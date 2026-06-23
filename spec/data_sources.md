# GSP Virtual Data Sources - Draft

Huge datasets should be modeled as virtual data sources, not ordinary buffers.

Examples:

- tiled image pyramids;
- cloud microscopy data;
- map tiles;
- point-cloud octrees;
- remote simulation timesteps;
- custom chunk APIs.

A data source should declare:

- logical shape;
- coordinate system;
- chunk/tile scheme;
- levels of detail;
- fetch locality;
- cache policy;
- credentials policy;
- materialization policy;
- query/readout behavior.

Remote renderers should be able to fetch data server-side when permitted, avoiding client data transfer.

## M011 v0.1 decision

Virtual data sources are core protocol objects, while concrete source kinds can be declared by
extension manifests. The first implemented source kind is `gsp.tiled-image@0.1`.

Implemented models:

- `DataSourceDescriptor`
- `TiledImageSource`
- `TileIndex`
- `TileRequest`
- `TileResult`
- `ViewportTileRequest`
- `ViewportMosaicResult`
- `TiledImageQueryPayload`
- `FakeTiledImageProvider`

Allowed executable localities in the v0.1 proof:

- `synthetic`
- `in-memory`

Credential policy for executable v0.1 proof:

- only `none`

Materialization policy for the reference proof:

- `viewport-mosaic`

The Matplotlib reference path materializes a deterministic viewport mosaic from the fake provider.
It does not perform network access, server-side fetch, asynchronous loading, cache eviction, or
Datoviz upload.

## M032 viewport edge semantics

For the local tiled-image proof, a `ViewportTileRequest.source_rect` may start outside the source
with negative x/y coordinates, provided width and height are positive. The fake provider clips the
requested source rectangle to the level-local source bounds before materialization.

Deterministic clipping rules:

- a partly out-of-bounds source rectangle produces a mosaic for the intersecting source region;
- `ViewportMosaicResult.source_rect` reports the clipped source rectangle;
- `tile_indices` contains only tiles intersecting the clipped source rectangle, ordered row-major;
- a source rectangle with no source intersection is not materialized.

Matplotlib reference rendering and tiled-image queries must use the same clipped source rectangle.
When clipping reduces the materialized source region, the rendered image extent is clipped
proportionally, and queries outside that clipped extent miss even if they are inside the originally
requested extent.

## M033 extension-source linkage

`TiledImageSource` is linked to the built-in static extension manifest by extension id and version.
The link is valid only when:

- the manifest kind is `data-source`;
- the source `extension_id` matches the manifest id;
- the source `extension_version` matches the manifest version;
- the manifest schema declares `source_kind="tiled-image"`;
- the manifest schema declares `credential_policy="none"`.

This validation is a local static check. It must not load plugins, run manifest code, or infer remote
data access behavior.

## M034 fixture coverage

The conformance fixture package includes a local tiled-source scene for S018 replay readiness. The
fixture locks:

- the built-in `gsp.tiled-image@0.1` static manifest;
- a synthetic `TiledImageSource`;
- a partially clipped `ViewportTileRequest`;
- deterministic `ViewportMosaicResult` tile ordering;
- Matplotlib reference rendering extent;
- typed `TiledImageQueryPayload` coordinates and value.

The fixture remains Python/in-process. JSON/base64 replay encoding is deferred to S018.

## S020 remote data security pre-design

Future remote-capable data sources are modeled as data-only descriptors. The descriptor vocabulary is
reserved before production fetch exists so validation, diagnostics, and conformance can reject unsafe
inputs deterministically.

Reserved `DataSourceDescriptor` fields:

- `id`;
- `kind`;
- `extension_id`;
- `schema_version`;
- `logical_shape`;
- `logical_dtype`;
- `coordinate_space`;
- `bounds`;
- `chunk_scheme`;
- `lod_scheme`;
- `source_locality`;
- `source_ref`;
- `fetch_descriptor`;
- `credential_policy`;
- `credential_ref`;
- `materialization_policy`;
- `cache_policy`;
- `query_contract`;
- `integrity_policy`;
- `resource_hints`;
- `diagnostics_policy`.

Executable localities for the current safe line are:

- `synthetic`;
- `in-memory`;
- optional `preconfigured-source`, where the client supplies only an opaque server-known handle.

Reserved or future localities are:

- `local-file-sandboxed`;
- `client-materialized`;
- `server-resolved-remote`;
- `direct-remote-fetch`;
- `browser-origin-fetch`.

The v0.2 default is to reject `fetch_descriptor` and every direct remote/local fetch shape,
including URL-like fields, object-store URIs, request headers, cookies, signed URLs, local paths, and
client-controlled retry or redirect policy.

`preconfigured-source` means:

- `source_ref` is opaque and resolver-scoped;
- unknown handles reject fatally;
- administrator or test configuration owns any underlying URL, path, bucket, or credential;
- the scene never serializes the underlying location or secret material;
- a no-network mock resolver is the preferred first proof.

Credential policies are:

- `none`: no credential is used;
- `preconfigured`: credentials, if any, are resolver-owned and absent from protocol payloads.

`preconfigured-ref`, `delegated`, and `inline` are not executable v0.2 policies. `inline` is always
invalid. `credential_ref`, if ever enabled, is an opaque selector, not a secret, and must be
resolver-, tenant-, and session-authorized.

Cache policies reserve:

- `mode`: `none`, `session-memory`, `private-persistent`, or `shared-readonly`;
- `scope`: `session`, `user`, `tenant`, or `public-immutable`;
- `max_bytes`;
- `max_items`;
- `ttl_seconds`;
- `immutable`;
- `key_fields`;
- `poisoning_policy`;
- `eviction_policy`.

The current safe cache modes are `none` and optionally `session-memory`. Shared or persistent cache
entries must not be used for mutable or credentialed data unless future validation binds keys to
tenant/session, resolver, source identity, credential identity/version marker, extension
id/version, decoder version, LOD, chunk coordinates, materialization parameters, and content
generation or digest.

Resource validation must reject non-finite or excessive logical shapes, tile sizes, LOD counts,
chunk counts, decompressed chunk sizes, per-frame tile counts, total materialized bytes, prefetch
concurrency, retry counts, and query result sizes before materialization.

Query/readback is scoped by `query_contract`. Results must be typed, bounded, and limited to
declared source bounds, viewport/panel selection, and extension payload schemas. Query results must
not expose server paths, URLs, credentials, resolver configuration, internal hostnames, tenant ids,
or cache internals.

Security-sensitive unsupported behavior rejects fatally. It must not silently clip, downgrade, or
simplify remote fetch, credentials, local paths, resource-limit violations, cache isolation failures,
or query-scope violations unless a query contract explicitly allows a clipped result with a
diagnostic.

## S021 no-network preconfigured-source resolver proof

The first implementation after S020 is a no-network resolver proof. It maps administrator/test
`source_ref` handles to deterministic local `TiledImageSource` objects and `FakeTiledImageProvider`
instances.

The proof resolver:

- accepts only `source_locality="preconfigured-source"` descriptors;
- accepts only advertised `{resolver_id, source_id}` handles;
- supports only tiled-image sources backed by synthetic or in-memory local providers;
- supports only `credential_policy="none"`;
- rejects `fetch_descriptor`, URL-like metadata, local paths, and credential references;
- advertises `network_io=false`;
- never opens files, resolves hosts, performs HTTP/object-store access, loads plugins, or uses
  Datoviz.

The built-in proof handle is:

```text
resolver_id = "gsp.test.synthetic-resolver"
source_id = "public-demo-pyramid"
```

## S022 HTTP single-resource `.npy` array architecture

ADR-0009 accepts HTTP single-resource as the first remote access architecture test, with `.npy`
typed array as the first source contract. This is a protocol and conformance baseline, not a
runtime network feature.

HTTP is an access mechanism, not a source kind. Scenes must not use `source_kind="http"`, and HTTP
details never belong in scene payloads. The first S022 source descriptor uses:

- `source_kind="array"`;
- `format="npy"`;
- `decoder_id="gsp.decoder.npy.v1"`;
- `locality="preconfigured-source"`;
- `credential_policy="none"`;
- opaque `source_ref.resolver_id` and `source_ref.source_id`;
- bounded `shape`, `dtype`, `channels`, and `coordinate_system="array-index"`;
- `materialization_policy="full"`;
- `materialization_target="array-resource"`;
- optional `cache_policy.mode` limited to `none` or `session-memory`;
- optional `extent` and `origin` only when a rank-2 array is adapted for image-like reference
  rendering.

The first executable proof must use a mock/configured HTTP access contract with `network_io=false`.
The stable mock identifiers are:

```text
access.mechanism = "http"
fetcher_id = "gsp.fetcher.http.mock.v1"
decoder_id = "gsp.decoder.npy.v1"
source_kind = "array"
materialization_target = "array-resource"
```

The private resolver/admin configuration, not the scene, owns:

- URL and host allowlist for any later real HTTP source;
- fetcher id and access mechanism;
- method, redirect policy, TLS policy, timeout, retry, content-type, content-encoding, and byte
  limits;
- decoder policy such as allowed dtypes, `.npy` versions, header size, rank, element count,
  decoded byte limit, and `allow_pickle=false`;
- credential policy, which is `none` for the first proof;
- cache mode, private cache-key material, authorization generation, source generation, and optional
  integrity digest;
- tenant/session/user authorization bindings.

These private resolver fields must not appear in scene payloads, manifests, diagnostics, fixtures,
debug JSON, replay artifacts, or public capability snapshots as raw values.

### First-proof descriptor rules

The first S022 descriptor accepts only the following scene-visible remote-array fields:

- `id`;
- `source_kind`;
- `extension_id`;
- `extension_version`;
- `shape`;
- `dtype`;
- `channels`;
- `coordinate_system`;
- `extent`;
- `origin`;
- `locality`;
- `credential_policy`;
- `source_ref.resolver_id`;
- `source_ref.source_id`;
- `format`;
- `decoder_id`;
- `cache_policy.mode`;
- `materialization_policy`;
- `materialization_target`;
- non-sensitive `metadata` under documented `x-` keys.

The following fields or field shapes are forbidden in scenes, manifests, fixtures, replay, and
client-supplied descriptors:

- `fetch_descriptor`;
- raw URL-like fields such as `url`, `uri`, `href`, `endpoint`, `host`, `port`, `path`, `bucket`,
  `object_key`, `signed_url`, or `query`;
- request metadata such as `headers`, `cookies`, or `authorization`;
- credentials such as `credential_ref`, `credentials`, `secret`, `token`, or `api_key`;
- decoder execution fields such as `decoder_config`, `decoder_module`, `decoder_import`,
  `python_import`, `entry_point`, `package`, `pip`, `callback`, `hook`, or `plugin`;
- shader or executable fields such as `shader`, `shader_source`, or `runtime_shader`;
- resolver-private fields such as `cache_key`, `resolved_url`, `dns_result`, `ip_address`,
  `etag_from_resolver`, or `private_digest`.

Unknown descriptor fields reject unless a future spec defines them or they live under an explicitly
non-executable `x-` namespace and still pass the sensitive-key, URL-like, path-like, credential, and
executable-field validators.

### `.npy` decoder policy

`gsp.decoder.npy.v1` is a trusted built-in decoder policy, not an import path or plugin. The first
proof must reject:

- pickle and object dtype;
- structured dtype;
- string, unicode, and void dtype;
- Fortran-order arrays;
- unknown or excessive rank;
- shape mismatch between scene, resolver config, and `.npy` header;
- decoded byte counts above the configured limit;
- header size above the configured limit;
- invalid magic, unsupported `.npy` version, unexpected header keys, trailing bytes, or
  non-executable-parser failures.

First-proof allowed dtypes are `uint8`, `uint16`, and `float32`. First-proof rank should be 2 or 3,
with the first fixture using rank 2.

### Cache and query policy

The default cache mode is `none`. `session-memory` may be used only when entries are isolated by
tenant/session, resolver id, source id, authorization generation, source contract, declared
shape/dtype/channels, access mechanism, fetcher id, credential policy, decoder id, decoder policy,
format, materialization target, byte/decode limit policy, and content generation or verified digest.

Cache keys and private cache hashes must not be serialized in diagnostics, fixtures, debug JSON, or
replay. Failed fetch/decode/materialization results are not cached in the first proof.

Array query/readback, when implemented, is bounded by declared shape and result-size limits. Query
payloads may report source id, array index coordinate, dtype, and value, but must not expose
resolver URLs, cache keys, digests, fetch metadata, hostnames, credentials, or private config.
