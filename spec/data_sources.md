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
