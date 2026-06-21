# Matplotlib Backend Spec - Draft

Matplotlib is the reference/conformance/publication backend.

Responsibilities:

- correctness over speed;
- small-scene conformance;
- PNG/SVG/PDF where possible;
- reference CPU query path;
- explicit diagnostics for unsupported behavior.

The backend should consume formal GSP models, not define protocol semantics.

## M003 reference slice

`gsp_matplotlib.protocol_renderer` renders the first formal protocol visual models:

- `PointVisual` to `matplotlib.collections.PathCollection`;
- `ImageVisual` to `matplotlib.image.AxesImage`.

This is a narrow conformance slice beside the legacy renderer. The legacy `MatplotlibRenderer` remains available for existing examples.

## M011 tiled-source reference proof

`gsp_matplotlib.tiled_image` materializes a `TiledImageSource` viewport mosaic through
`FakeTiledImageProvider` and renders it via the existing image protocol renderer. It also provides a
reference tiled-image query helper that returns normal `QueryResult` fields plus
`TiledImageQueryPayload`.
