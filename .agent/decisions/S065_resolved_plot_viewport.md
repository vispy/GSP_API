# S065 Resolved Plot-Viewport Boundary

Status: accepted for M286 on 2026-07-25.

## Decision

GSP uses the existing resolved-layout model; this decision does not introduce a second layout
system.

- `Panel.viewport_rect` allocates the outer panel inside the resolved render target.
- `ResolvedLayoutSnapshot.panel_rect_px` is the complete panel presentation and guide-query region.
- `ResolvedLayoutSnapshot.plot_rect_px` is the contained visual/data viewport after guide and
  layout allocation.
- DATA and panel-NDC visual positions map through `plot_rect_px`.
- Data queries, View3D rays, mesh picking, and layout-dependent navigation use `plot_rect_px`.
  Coordinates in the panel but outside the plot cannot hit data visuals; resolved guide boxes there
  remain queryable.
- Perspective `aspect_ratio=None` resolves from plot width divided by plot height. An authored
  positive aspect remains explicit. The projection snapshot records the effective value and its
  provenance, and its identity includes the effective plot geometry.
- `PanelTextGuide` remains a guide. Missing rendering support produces a diagnostic and does not
  allow a backend to reclaim the guide lane or change data scale.
- Layout-strict or cross-backend comparison produces one snapshot that every backend consumes.
  Semantic-only operation may remain backend-resolved with diagnostics.

## Producer/Consumer Staging

M286 implements and tests the backend-neutral producer boundary: rectangle validation, logical
pixel/panel-NDC conversion, data-viewport containment, plot-aspect resolution, and View3D
projection snapshot identity.

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

## Deferred

- Public multi-panel layout authoring and panel-to-view collection schemas.
- Font measurement, text shaping, and cross-backend font-metric resolution.
- Backend layout consumption and native guide realization, assigned to M287.
- Datoviz and VisPy2 changes.
