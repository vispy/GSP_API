# S065 Resolved Plot-Viewport Boundary

Status: accepted for M286 on 2026-07-25.

## Decision

GSP uses the existing resolved-layout model; this decision does not introduce a second layout
system.

- `Panel.viewport_rect` allocates the outer panel inside the resolved render target. Its four
  components are finite normalized values; x/y are nonnegative, width/height are positive, and
  closed containment requires `x + width <= 1` and `y + height <= 1`. For target `(W,H)`, it
  resolves deterministically to `(x*W, y*H, width*W, height*H)`.
- `ResolvedLayoutSnapshot.panel_rect_px` is the complete panel presentation and guide-query region.
- `ResolvedLayoutSnapshot.plot_rect_px` is the contained visual/data viewport after guide and
  layout allocation.
- DATA and panel-NDC visual positions map through `plot_rect_px`.
- Data queries, View3D rays, mesh picking, and layout-dependent navigation use `plot_rect_px`.
  Coordinates in the panel but outside the plot cannot hit data visuals; resolved guide boxes there
  remain queryable.
- Public pointer/query logical coordinates are absolute render-target coordinates. Closed plot
  containment preserves exact NDC edges for both pixel origins; raster ownership may be half-open.
- `RenderTarget.pixel_origin` is a validated `PixelOrigin` value. Valid enum strings may be
  explicitly coerced; invalid strings and types are rejected.
- Coordinates classify as outside panel, panel guide lane, or data plot. Guide-lane DATA queries
  miss, guide scopes remain eligible, and rays/picks/navigation never extrapolate or clamp them.
- The outer panel has positive area. A degenerate plot contains no data and cannot supply
  conversion, aspect, or navigation geometry.
- Perspective `aspect_ratio=None` resolves from plot width divided by plot height. An authored
  positive aspect remains explicit. The projection snapshot records the effective value and its
  provenance, and its identity includes the effective plot geometry.
- `PanelTextGuide` remains a guide. Missing rendering support produces a diagnostic and does not
  allow a backend to reclaim the guide lane or change data scale.
- Layout-strict or cross-backend comparison produces one snapshot that every backend consumes.
  Semantic-only operation may remain backend-resolved with diagnostics.
- View2D layout-aware pan and zoom use the snapshot plot rectangle and pixel origin. Top-left and
  bottom-left origins invert vertical pan sign and make a top-edge zoom preserve `y_max` and
  `y_min`, respectively. Existing rect-only helpers remain compatible but are not origin-strict.

## Producer/Consumer Staging

M286 implements and tests the backend-neutral producer boundary: rectangle validation, logical
pixel/panel-NDC conversion, typed coordinate routing, plot-aspect resolution, navigation freshness,
View3D projection snapshot identity, normalized panel-intent resolution, pixel-origin validation,
and origin-aware View2D navigation. Navigation scaling consumes plot width/height.

M287 connects the produced snapshot to Matplotlib and Datoviz render, query, and readback consumers.
Backend consumption must not substitute native axes rectangles, full-canvas rectangles, gallery
scale constants, camera margins, or backend-specific aspect overrides.

Later conformance promotion may claim layout strictness only after render and every applicable
query/readback path prove the same snapshot identity.

## Compatibility

Existing View3D callers that provide only `layout_snapshot_id` remain accepted. When a perspective
projection has no authored aspect, that path resolves the historical aspect `1.0`, records
`compatibility_default` provenance, and emits a missing-layout-geometry diagnostic. It is not a
layout-strict result.

Existing rect-only View2D navigation callers retain their historical vertical mapping. Supplying a
resolved layout makes both `plot_rect_px` and its `pixel_origin` authoritative.

## Deferred

- Public multi-panel layout authoring and panel-to-view collection schemas.
- Aggregate/multi-panel resolved-layout snapshots; the core snapshot remains single-panel.
- Font measurement, text shaping, and cross-backend font-metric resolution.
- Backend layout consumption and native guide realization, assigned to M287.
- Datoviz and VisPy2 changes.
