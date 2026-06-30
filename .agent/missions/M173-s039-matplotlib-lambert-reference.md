# M173 - S039 Matplotlib Lambert reference behavior

## Stage

S039 - Lambert Normals Pre-Design

## Status

Ready.

## Summary

Implement the S039 flat Lambert material math in the Matplotlib/reference path without claiming
strict GPU-style 3D raster conformance.

## Deliverables

- Resolve S039 flat Lambert face colors from canonical protocol fields.
- Preserve Matplotlib's adapted 3D projection/depth boundary.
- Add focused tests for explicit normals, generated normals, ambient-only, directional-only,
  back-facing clamp, winding reversal, and alpha passthrough diagnostics where applicable.
- Keep backend-native/legacy material classes private and unused as public protocol authority.

## Acceptance

- Material math follows ADR-0026 and `spec/visuals/mesh_flat_lambert_s039.md`.
- Matplotlib can render/review flat Lambert by passing resolved face colors to the existing mesh path.
- The backend does not advertise stricter 3D raster/depth semantics than existing S036/S037 support.

## Stop Condition

Stop if implementing Matplotlib Lambert requires changing accepted public protocol fields or reviving
legacy public material/light classes.
