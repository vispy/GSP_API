# Resolved Layout, Logical Pixels, And Guide Geometry

Status: accepted direction for S029/S034 from ADR-0020 and P016. This file defines the protocol
foundation; backend reference implementations are follow-up work.

## Conformance Tiers

GSP separates guide meaning, resolved geometry, and raster output:

- `semantic_strict`: scene semantics match. Views, domains, visual identities, guide identities,
  roles, labels, deterministic tick intent, grid intent, supported query payloads, and capability
  diagnostics are protocol-stable. Pixel-identical placement is not required.
- `layout_strict`: render, query, readback, and all-rendered contributions use the same
  `ResolvedLayoutSnapshot`. Panel rectangles, plot rectangles, guide boxes, title boxes, axis lanes,
  tick label boxes, legend/colorbar boxes, grid clipping, data-to-screen transforms, and
  `layout_snapshot_id` must match within geometric tolerance.
- `raster_tolerant`: layout geometry and nominal logical sizes match, while glyph rasterization,
  antialiasing, hinting, and small subpixel differences remain tolerant.
- `pixel_parity`: optional opt-in tier for jobs that intentionally require raster-level parity.

Semantic strictness does not imply visual parity. Layout strictness means matching GSP resolved
layout, not matching Matplotlib quirks by accident.

## Render Target

All `*_px` layout and guide style values are logical pixels unless a field explicitly says
otherwise. A `RenderTarget` records:

- `logical_width_px`;
- `logical_height_px`;
- `device_scale`;
- `dpi`;
- `pixel_origin`;
- `query_coordinate_space`.

Physical framebuffer size is derived as:

```text
framebuffer_width_px = logical_width_px * device_scale
framebuffer_height_px = logical_height_px * device_scale
```

Queries default to logical panel pixel coordinates. Backend physical pixels and DPI metadata must not
silently change logical layout sizes.

Matplotlib converts logical pixels to typographic points with:

```text
points = logical_px * 72 / dpi
```

Datoviz adapters should map logical pixels to backend pixels through `device_scale` unless the
Datoviz windowing layer already reports logical window pixels. That choice must be diagnosed until
proven.

## Resolved Layout Snapshot

`ResolvedLayoutSnapshot` is a derived protocol artifact for one scene, view, render target, font
context, and layout policy. It must be inspectable where layout strictness is advertised.

`Panel.viewport_rect` is authoring input that allocates the outer panel within the resolved render
target. Each of its four normalized components is finite; x/y are nonnegative, width/height are
positive, and closed containment requires `x + width <= 1` and `y + height <= 1`. For logical
target size `(W,H)`, the outer panel resolves deterministically to
`(x*W, y*H, width*W, height*H)`. The snapshot makes the resulting boundary executable:

- `panel_rect_px` is the full presentation region for the panel, including guide lanes and the
  guide-query region;
- `plot_rect_px` is the visual/data viewport after guide and layout allocation.

Both rectangles have finite, nonnegative coordinates and extents, are contained by the logical
render target, and `plot_rect_px` is contained by `panel_rect_px`. The outer panel has positive
area. A zero-area plot can represent an allocated-but-inactive data region, contains no data, and
is rejected by projection conversion, navigation, and aspect helpers.

Minimal fields:

- `snapshot_id`;
- `render_target`;
- `panel_rect_px`;
- `plot_rect_px`;
- `view_id`;
- `data_to_screen_transform`;
- `guide_boxes`;
- `guide_anchors`;
- `tick_label_boxes`;
- `axis_label_boxes`;
- `title_boxes`;
- `legend_boxes`;
- `colorbar_boxes`;
- `grid_clip_rect_px`;
- `z_layers`;
- `diagnostics`.

The data-to-screen transform maps accepted data coordinates into logical pixel coordinates for the
resolved plot rectangle. Reversed `View2D` limits are represented in that transform rather than by
changing semantic domains.

Public logical pointer and query coordinates are absolute render-target logical coordinates. DATA
positions and panel NDC map through `plot_rect_px`, never through the complete canvas or
`panel_rect_px`. Panel NDC has `x=-1` at the plot left, `x=+1` at the plot right, `y=-1` at the plot
bottom, and `y=+1` at the plot top. Logical-pixel conversion honors the render target's declared
pixel origin: top-left origin maps plot top-left to `(-1,+1)` and bottom-right to `(+1,-1)`;
bottom-left origin reverses y. The protocol exposes typed conversions between render-target logical
coordinates and plot-relative panel NDC, a resolved plot-aspect helper, and a three-way classifier
for outside-panel, panel-guide-lane, and data-plot coordinates.

`RenderTarget.pixel_origin` is validated as `PixelOrigin.TOP_LEFT` or
`PixelOrigin.BOTTOM_LEFT`; implementations may explicitly coerce the corresponding string values,
but unknown strings and non-enum types are invalid and must never fall through to bottom-left
behavior.

Geometric containment is closed, including exact rectangle edges, to preserve exact NDC edge round
trips. Raster sample ownership may remain backend-private and half-open. Plot conversion rejects a
guide-lane coordinate rather than extrapolating NDC.

Data queries, View3D rays, mesh picking, and layout-dependent navigation use `plot_rect_px`. A
coordinate may therefore be inside the outer panel but outside the data viewport. Such a coordinate
cannot hit a data visual, although a guide query may hit a resolved guide box there.
Supported DATA queries there return MISS; GUIDE and ALL_RENDERED queries may still hit guide boxes.
No View3D ray, mesh pick, pointer anchor, or zoom anchor is clamped or extrapolated from that lane.

Grid lines are clipped to `plot_rect_px` in layout-strict mode unless a future spec defines an
explicit alternate policy. A white overlay band that hides grid lines is a review artifact, not a
layout-strict grid clipping proof.

## Guides

Guides remain guides even when a backend realizes them with native axes, text primitives, image
ramps, or other visuals.

`PanelTextGuide(role=TITLE)` must not be silently lowered to an ordinary `TextVisual` in
conformance mode. An adapter may render it through screen text only as an explicit adaptation such
as:

```text
adapted: panel_text_guide_as_screen_text
```

Axis, title, legend, and colorbar layout should follow the same model:

1. semantic guide record as input;
2. resolved boxes/anchors/lanes/ramp/ticks as layout output;
3. query/readback contribution using the same layout snapshot where advertised.

A colorbar is a guide associated with a color scale. Its ramp rectangle, ticks, labels, title/label,
and query behavior must be inspectable when layout/query support is advertised.

## Guide Style Fields

The protocol reserves logical-pixel guide style fields:

- `title_font_size_px`;
- `axis_label_font_size_px`;
- `tick_label_font_size_px`;
- `tick_length_px`;
- `tick_width_px`;
- `tick_label_padding_px`;
- `axis_label_padding_px`;
- `grid_width_px`;
- `guide_margin_px`.

Unspecified style values may use backend defaults in semantic mode. In layout mode, selected values
must be resolved/read back or reported through diagnostics such as `backend_default_used`,
`font_substituted`, or `missing`.

## Operations And Snapshot Identity

The protocol model includes records equivalent to:

- `layout/resolve`;
- `layout/get`;
- `render.layout_snapshot_id`;
- `query.layout_snapshot_id`.

Exact transport command names may evolve, but the semantic requirement is fixed: render, query,
readback, and all-rendered guide contributions must identify the same `layout_snapshot_id` whenever
a backend advertises layout-strict behavior.

Layout-strict and cross-backend comparison produce one `ResolvedLayoutSnapshot` and require every
backend to consume it. Semantic-only operation may allow backend-resolved layout with diagnostics.
Guide support does not alter geometry consumption: if a backend cannot render a
`PanelTextGuide`, it consumes the same plot rectangle and reports the missing guide instead of
expanding the plot into the reserved lane.

The core `ResolvedLayoutSnapshot` represents one panel/view boundary. Aggregate snapshot containers
and public multi-panel layout authoring remain deferred.

## Capability Surface

Capability snapshots distinguish layout support from raster parity.

Layout:

- `semantic_guides`;
- `resolved_layout_produce`: `none | partial | full`;
- `resolved_layout_consume`: `none | partial | full`;
- `layout_strict`;
- `raster_pixel_parity`.

Guides:

- axis native/explicit ticks/deterministic GSP ticks/labels/grid/grid clipping/query;
- panel title realization and whether it participates in layout/query;
- colorbar realization and query;
- legend realization and query.

Fonts:

- logical font size support;
- font family request support;
- font fallback reporting;
- text measurement mode;
- font metrics profile;
- rasterization parity.

Render target:

- logical pixels;
- device scale;
- DPI metadata;
- physical framebuffer scale.

Query:

- logical screen-pixel query coordinates;
- data readout using the view snapshot;
- guide query;
- all-rendered guide query;
- `layout_snapshot_id` reporting.

Recommended diagnostic statuses include `native`, `resolved`, `adapted`, `degraded`, `unsupported`,
`missing`, `backend_default_used`, `font_substituted`, `layout_snapshot_not_used`,
`query_semantics_missing`, and `grid_clip_not_enforced`.

## Backend Posture

Matplotlib is the initial publication/reference backend for layout-strict behavior, but
Matplotlib's native layout engine is not itself the GSP contract. It must expose the resolved GSP
layout snapshot it used before claiming layout strictness.

Datoviz remains the high-performance GPU backend. Until it can produce or consume resolved layout
snapshots and query guide geometry, it should advertise semantic/adapted guide support and must not
claim layout strictness. Current adapted review rows should diagnose title screen-text adaptation,
missing guide query, and missing all-rendered guide contributions. Grid clipping is reported
independently: verified Datoviz builds may advertise native plot-rect grid clipping evidence, while
older or unverified builds must keep explicit grid clipping blockers.

## Visual QA

Review packs must distinguish:

- semantic guide QA;
- resolved layout QA;
- raster tolerant QA;
- adapted review artifacts.

Adapted rows may be useful review artifacts, but they must not count as layout-strict passes.
