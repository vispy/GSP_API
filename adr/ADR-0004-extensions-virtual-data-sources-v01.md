# ADR-0004 - Minimal extension and virtual data-source model for v0.1

## Status

Accepted

## Context

GSP v0.1 has an accepted vertical slice: protocol IDs, capability snapshots, contiguous
in-process buffers, local transport without mandatory JSON/base64, point/image visual models,
Matplotlib reference rendering, deterministic reference query, a bounded Datoviz v0.4 adapter
slice, and a minimal VisPy2 producer MVP.

The project also needs a path for huge datasets that should not be represented as ordinary eager
buffers, including tiled image pyramids, cloud microscopy images, map tiles, point-cloud octrees,
and remote simulation timesteps.

This architecture is high-risk because it can easily expand into a plugin platform, credential
manager, cloud client, async scheduler, or distributed renderer. M011 therefore used ChatGPT Pro
consultation packet `P001` before implementation.

## Decision

GSP v0.1 introduces a minimal, static extension and virtual data-source proof:

- `ExtensionManifest` is static metadata. It is not a dynamic plugin loader and does not execute
  code.
- Virtual data sources are core protocol objects, while concrete source kinds may be declared by
  extension manifests.
- The first built-in reference extension is `gsp.tiled-image@0.1`.
- The first executable source model is `TiledImageSource`, backed only by synthetic or in-memory
  local data in v0.1.
- `TileRequest`, `TileResult`, `ViewportTileRequest`, and `ViewportMosaicResult` define a local
  in-process materialization path with direct NumPy arrays.
- Matplotlib reference behavior materializes a deterministic viewport mosaic and renders it through
  the existing image visual path.
- Tiled-image query returns normal `QueryResult` fields plus a typed extension payload
  `TiledImageQueryPayload`.

The local fast path remains direct Python/NumPy objects. JSON/base64 remains secondary for future
fixtures, debugging, or replay only.

## In scope

- Static extension manifest dataclasses.
- Core data-source descriptors and references.
- Built-in `gsp.tiled-image@0.1` source kind.
- Synthetic/in-memory fake tiled image provider.
- Matplotlib reference materialization of viewport mosaics.
- Tiled-image reference query payload with source/tile/texel coordinates.
- Capability fields and extension adaptation helpers.
- Tests that verify deterministic local materialization and query behavior.

## Out of scope

- Dynamic plugin discovery or loading.
- Python entry-point/package-manager integration.
- Runtime shader extension loading.
- Real HTTP, S3, GCS, Zarr, OME-Zarr, COG, or map-tile clients.
- Secret storage, credential exchange, or URL credential handling.
- Async tile loading, prefetch, LRU cache, retry logic, or progressive refinement.
- Production server-side fetch.
- Remote renderer implementation.
- Datoviz tiled-image support.
- User-facing VisPy2 cloud/tiled API.

## Consequences

GSP now has a protocol-level place for huge data without committing to a production remote data
platform. Backends can explicitly advertise or reject `gsp.tiled-image@0.1`. The Matplotlib proof
locks the intended semantics in tests while keeping Datoviz and VisPy2 untouched.

The new abstraction introduces a second path for image-like data: eager `ImageVisual.image` and
virtual tiled sources. The boundary is explicit: data sources describe availability and
materialization; visuals keep placement, interpolation, origin, and semantic image behavior.

## Open questions

- Whether future image visuals should carry a `data_source_ref` directly or use a separate command
  graph binding.
- Exact future serialized fixture format for data-source descriptors.
- Future security model for preconfigured server-side credentials.
- Future Datoviz mapping for tiled images, sampled fields, or streaming texture updates.
