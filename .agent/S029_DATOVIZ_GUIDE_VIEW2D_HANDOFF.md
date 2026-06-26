# Datoviz Guide/View2D Handoff for S029

Updated: 2026-06-26

## Context

GSP S029 keeps Datoviz guide/View2D rows unsupported:

- `guide/view2d_auto_grid`
- `guide/view2d_reversed_explicit`

Datoviz v0.4-dev exposes a native panel axis surface that GSP can use for a bounded adapted proof,
but GSP does not yet have enough rendered/runtime evidence to promote semantic guide rows.

## Required Evidence Before GSP Promotion

Datoviz-side or GSP/Datoviz integration work should prove:

1. Backend auto tick rendering aligns with the same `View2D` snapshot used for DATA visual mapping.
2. Explicit GSP tick values and labels can be applied exactly to Datoviz panel axes.
3. Reversed finite `View2D` domains render ticks and grid lines in reversed panel direction without
   changing tick identity.
4. Axis labels, panel titles, grid visibility, and layout do not silently overlap or drift from the
   GSP guide contract.
5. Guide picking/query or a documented unsupported query diagnostic exists for axis ticks, grid,
   labels, and panel titles before `guides` or `all-rendered` query support is advertised.

## Current GSP Position

Until that evidence exists, GSP should keep both S029 Datoviz guide rows:

- `status: unsupported`
- `rendering_supported: false`
- `query_supported: false`
- `reason_code: datoviz_axis_guide_contract_unverified`

Do not promote by approximating tick labels, reversed domains, titles, grid placement, or guide query
payloads.
