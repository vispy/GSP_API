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
