# M097 - S026 Datoviz runtime scalar color slice

## Stage

S026 - Color Mapping, Colorbars, and Scalar Data Semantics

## Status

Approved.

## Summary

Implement or explicitly capability-gate a narrow Datoviz v0.4 runtime slice for accepted S026
scalar color behavior.

## Context

S026 public semantics are already accepted by P011/M091. M092-M096 added protocol validation,
Matplotlib reference behavior, visual QA/examples, Datoviz capability evidence, and VisPy2 producer
APIs. M095 found local Datoviz runtime candidates for scales, accepted colormaps including gray,
scalar sampled fields, visual scale binding, colorbars, point scalar colors, and query APIs.

This mission is implementation work, not protocol design.

## Planned Deliverables

- Datoviz adapter support or structured unsupported diagnostics for scalar `ImageVisual` color-scale
  rendering.
- Datoviz adapter support or structured unsupported diagnostics for `PointVisual` scalar color
  rendering.
- Datoviz handling or structured unsupported diagnostics for semantic `ColorbarGuide` rendering.
- Datoviz query/readback support or structured unsupported diagnostics for S026 scalar query payloads.
- Focused tests that skip cleanly when local Datoviz runtime/offscreen execution is unavailable.
- Updated mission/task notes documenting verified capabilities and remaining gates.

## Acceptance

- Implemented behavior follows `spec/color_mapping.md`, `spec/backends/datoviz.md`, and
  `spec/backend_capabilities_visuals.md`.
- No public S026 protocol/API semantics are changed.
- Marker scalar fill and mesh face scalar colors remain capability-gated unless native Datoviz
  contracts are verified inside this mission.
- Unsupported behavior emits existing structured diagnostics rather than silent fallback.
- Tests cover implemented paths and capability-gated paths.

## Stop Conditions

- Stop if Datoviz behavior requires changing accepted S026 semantics.
- Stop if native Datoviz APIs cannot be verified well enough to distinguish strict support from
  lossy adaptation.
- Stop before broad colormap registries, nonlinear normalization, legends, layout systems, marker
  stroke scalar colors, segment/path scalar colors, text scalar colors, or mesh scalar shading.
