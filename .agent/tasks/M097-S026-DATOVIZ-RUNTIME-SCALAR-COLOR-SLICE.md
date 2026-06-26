# M097-S026 - Datoviz runtime scalar color slice

## Mission

M097

## Goal

Implement or explicitly capability-gate the narrow accepted S026 scalar color runtime slice in the
Datoviz v0.4 adapter.

## Status

Approved.

## Deliverables

- Pending: scalar `ImageVisual` color-scale runtime path or structured unsupported diagnostic.
- Pending: `PointVisual` scalar color runtime path or structured unsupported diagnostic.
- Pending: `ColorbarGuide` runtime handling or structured unsupported diagnostic.
- Pending: scalar query/readback payload runtime handling or structured unsupported diagnostic.
- Pending: focused tests with clean skips for unavailable Datoviz runtime/offscreen execution.
- Pending: closeout notes for verified capabilities and remaining gates.

## Notes

- P011/M091 already accepted the public S026 color mapping/colorbar/scalar query semantics.
- M095 found candidate Datoviz runtime APIs for scales, accepted colormaps, scalar sampled fields,
  visual scale binding, colorbars, point scalar colors, and query APIs.
- Marker scalar fill and mesh face scalar colors stay capability-gated unless runtime contracts are
  verified during this mission.

## Acceptance

- Follows `spec/color_mapping.md`, `spec/backends/datoviz.md`, and
  `spec/backend_capabilities_visuals.md`.
- Does not alter public protocol or VisPy2 API semantics.
- Emits structured diagnostics for unsupported or lossy behavior.

## Stop Conditions

- Stop if implementation requires changing accepted S026 semantics.
- Stop if Datoviz runtime behavior is too ambiguous to claim strict support.
- Stop before expanding into deferred scalar slots, legends, broad colormap registries, nonlinear
  normalization, layout, or mesh shading.
