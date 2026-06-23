# M066-S023-POINTVISUAL-V1-DATOVIZ-V04-RETAINED-POINT-PATH - PointVisual v1

## Mission

M066

## Goal

Make PointVisual the first complete S023 visual-family proof: stable protocol semantics,
Matplotlib reference rendering, Datoviz v0.4 retained-scene adapter, tests, and visual QA cases.

## Required Inputs

- M064 Datoviz probe.
- M065 visual QA harness.
- `.agent/consultations/P008-response.md`, especially Point contract and cross-cutting rules.

## Contract Decisions To Apply

- `PointVisual.positions`: finite float32/float64, shape `(N, 2)` or `(N, 3)`.
- `PointVisual.colors`: per-point RGBA, uint8 `[0, 255]` or float `[0.0, 1.0]`.
- `PointVisual.sizes`: scalar or per-point rendered diameter in screen pixels.
- `coordinate_space`: keep `NDC` and `DATA`; S023 first Datoviz proof should prioritize NDC.
- Matplotlib scatter `s` is area, so convert protocol diameter pixels to Matplotlib area using
  figure DPI; do not leak Matplotlib `s` semantics into the protocol.
- Datoviz point path:
  - `PointVisual.colors -> uint8 RGBA8`
  - `PointVisual.sizes -> float32 diameter array`
  - `PointVisual.positions -> float32 vec3 positions`
  - create with `dvz_point(scene, flags)`
  - upload `"position"`, `"color"`, `"diameter_px"`
  - add to panel with explicit attach descriptor and z layer.

## Deliverables

- Spec/ADR updates for point and screen-space size units.
- Matplotlib renderer update if needed for pixel-diameter semantics.
- Datoviz v0.4 point adapter or renderer slice, capability-gated by M064.
- QA cases:
  - `point/basic_ndc`
  - `point/diameter_ramp_ndc`
  - `point/alpha_overlap_ndc` if alpha handling is already clear.
- Tests:
  - validation for point fields;
  - Matplotlib conversion behavior;
  - Datoviz adapter calls using fake facade;
  - unsupported diagnostics when symbols/capture are missing;
  - banned v0.3 symbol regression.

## Acceptance

- `uv run ruff check`, focused pytest, full pytest, and strict mypy pass.
- QA harness produces Matplotlib point PNGs.
- Datoviz produces a point PNG or structured unsupported report with precise missing capability.
- No dependency on legacy `gsp_datoviz.renderer`.

## Stop Conditions

- Stop if PointVisual semantics drift into marker/stroke/scalar-colormap scope.
- Stop if Datoviz coordinate-space mapping cannot be verified; record blocker and keep Matplotlib
  reference work separate.

## Completed

Completed on 2026-06-23.

- Accepted `PointVisual.sizes` as rendered screen-pixel diameters.
- Added ADR-0010 and updated point/Datoviz specs.
- Hardened PointVisual finite-value validation.
- Updated Matplotlib and Datoviz protocol renderers for diameter semantics.
- Added explicit Datoviz visual attach descriptors for the retained point path.
- Added `point/alpha_overlap_ndc` QA coverage.
- Verified Matplotlib and Datoviz point QA rendering.
