# S029 Datoviz Rendered-Family Promotion Audit

Updated: 2026-06-26

## Scope

Mission M113 audited only the Datoviz rendered families listed in the mission scope:

- point
- marker
- segment
- path
- image
- overlay

The audit used `artifacts/visual_qa/s029/current-review-pack` regenerated with the local Datoviz
`v0.4-dev` checkout after the explicit colorbar tick API fix.

## Promotion Decision

The following Datoviz rows are promoted to `strict` for rendering only, with reason code
`datoviz_rendered_strict_s029_family_audit`:

| Family | Rows | Strict scope |
|---|---|---|
| point | `point/basic_ndc`, `point/diameter_ramp_ndc`, `point/alpha_overlap_ndc` | NDC positions, RGBA8 colors, pixel diameters, alpha overlap |
| marker | `marker/shapes_ndc`, `marker/angle_size_stroke_ndc` | NDC positions, RGBA8 fill/stroke, marker shape, angle, pixel size |
| segment | `segment/width_cap_ndc`, `segment/alpha_order_ndc` | NDC endpoints, RGBA8 color, stroke width, cap style, alpha/layering |
| path | `path/subpaths_width_join_ndc` | NDC path vertices, subpaths, stroke width, caps, joins |
| image | `image/checker_nearest_ndc`, `image/origin_lower_ndc`, `image/scalar_gray_clim_ndc`, `image/rgba_alpha_ndc` | NDC extent, upper/lower origin, nearest sampling, RGBA8, alpha, scalar gray/clim CPU mapping |
| overlay | `overlay/point_over_image_ndc` | Point-over-image NDC layering |

All promoted rows keep `query_supported: false`; this review pack proves rendered output, not
Datoviz query/readback payload parity.

## Rows Left Adapted

Rendered Datoviz rows outside M113 scope remain `adapted` pending focused audits:

- text: placement, anchors, font-size, DATA mapping, Unicode/multiline, rotation, and query semantics
- mesh: indexed/uniform/per-face 2D rendering and query/readback semantics
- color: scalar point/marker/image color mapping, colorbar ticks/labels, and scalar query payloads
- transform: inline/named transform and View2D parity across visual families

Guide rows remain `unsupported` because Datoviz axis guide, title, grid, explicit tick label, and
guide query semantics are still unverified.

## Datoviz Colorbar Tick Fix

The upstream Datoviz WIP crash was resolved before regenerating the pack:

- `_colorbar_resolve_ticks()` now falls back to `_colorbar_compute_ticks()` instead of recursing.
- Colorbar visual preparation now resolves explicit ticks instead of always computing automatic
  ticks.
- The Python array facade now exposes `dvz_colorbar_set_ticks(colorbar, values, labels=None)`.

GSP now calls `dvz_colorbar_set_ticks()` when `ColorbarGuide.ticks` are present, but color/colorbar
rows remain adapted until a separate color/colorbar audit promotes that broader scope.

