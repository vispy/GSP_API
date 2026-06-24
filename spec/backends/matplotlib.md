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
- `MarkerVisual` to shaped `matplotlib.collections.PathCollection` markers;
- `PathVisual` subpaths to open `matplotlib.patches.PathPatch` artists;
- `ImageVisual` to `matplotlib.image.AxesImage`.

This is a narrow conformance slice beside the legacy renderer. The legacy `MatplotlibRenderer` remains available for existing examples.

For `ImageVisual`, scalar images use the bounded v1 scalar mapping: gray colormap by default, optional explicit `clim`, explicit `origin`, and explicit `extent`. RGB/RGBA images bypass scalar colormap/clim.

For `MarkerVisual`, protocol sizes are screen-pixel diameters and are converted to Matplotlib scatter
area units with the active figure DPI, matching `PointVisual`. Marker `stroke_width` is also a
protocol pixel width and is converted to Matplotlib point linewidth using the active figure DPI. The
reference path supports the conservative v1 shapes `disc`, `square`, `triangle`, `diamond`, and
`cross`, plus scalar or per-marker angles in radians.

For `PathVisual`, protocol widths are screen-pixel stroke widths and are converted to Matplotlib
point linewidths using the active figure DPI. Each subpath is rendered as an open path patch so
Matplotlib can preserve cap and join styles without treating path interiors as independent
segments.

## M011 tiled-source reference proof

`gsp_matplotlib.tiled_image` materializes a `TiledImageSource` viewport mosaic through
`FakeTiledImageProvider` and renders it via the existing image protocol renderer. It also provides a
reference tiled-image query helper that returns normal `QueryResult` fields plus
`TiledImageQueryPayload`.

## M032 clipped tiled-source extent

When a tiled-source viewport source rectangle is partially outside source bounds, the Matplotlib
reference path renders only the clipped mosaic. The rendered `AxesImage` extent is clipped
proportionally to match the clipped source rectangle, and `query_tiled_image_source()` uses the same
clipped extent for hit testing and payload coordinates.
