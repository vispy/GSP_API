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

## S027 transform/view reference target

Matplotlib is the strict reference backend for accepted S027 semantics. It must implement finite
invertible 2D affine visual transforms, deterministic linear `View2D`, reversed limits, DATA/NDC
behavior, clipping after view mapping, accepted family-specific transform rules, and
`gsp.transform-query@0.1` inverse payloads for the strict 2D subset.

Matplotlib native transform objects are implementation details. They must not appear in protocol
records, fixtures, query payloads, or VisPy2 public API.

## S028 guide/View2D reference target

Matplotlib is also the strict reference backend for semantic guide consumption of `View2D`.

Reference guide rendering/query must:

- resolve x guide ticks from `View2D.xlim` and y guide ticks from `View2D.ylim`;
- accept reversed finite limits and render/query tick values through the original axis direction;
- preserve explicit tick values and labels exactly;
- use GSP deterministic auto ticks rather than Matplotlib locators as semantic authority;
- use the same `View2D` snapshot for guide rendering, guide-scoped query, all-rendered query, and
  data readouts.

Matplotlib axis artists remain backend realization details, not public protocol objects.

## S029/S034 resolved layout reference

Matplotlib can produce a `ResolvedLayoutSnapshot` from a drawn reference figure through
`gsp_matplotlib.layout.resolve_matplotlib_layout_snapshot()`. The snapshot exposes the native
Matplotlib artist geometry used for publication output as GSP logical-pixel rectangles:

- render target and DPI metadata;
- full panel rectangle;
- axes plot rectangle;
- title, axis-label, and tick-label boxes;
- grid clip rectangle equal to the resolved plot rectangle;
- affine data-to-logical-screen transform;
- guide z/layer records.

This is an extraction of the reference layout result, not a declaration that Matplotlib's
implementation details are the protocol contract. The backend advertises full resolved-layout
production but does not claim `layout_strict` until render, query, readback, and all-rendered guide
contributions all report and consume the same `layout_snapshot_id`.
