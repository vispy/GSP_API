# M172 - S039 protocol dataclasses and validation

## Stage

S039 - Lambert Normals Pre-Design

## Status

Ready.

## Summary

Implement the accepted S039 public protocol model and validation for flat Lambert face-normal mesh
shading.

## Deliverables

- Public protocol dataclasses/enums/fields for canonical S039 shading and lights.
- Validation for face normals, generated normals, DATA-space `(N,3)` requirements, light values, and
  legacy/deferred inputs.
- Capability names and diagnostics exported through the existing protocol surface.
- Focused unit tests for accepted and rejected S039 protocol inputs.

## Acceptance

- Implementation matches ADR-0026 and `spec/visuals/mesh_flat_lambert_s039.md`.
- `shading="flat_lambert"` rejects missing `View3D`, `(N,2)` positions, NDC positions, vertex
  normals, invalid normals, invalid generated normals, and invalid light parameters.
- No backend-native material, shader, draw-state, artist, or legacy material class becomes public
  protocol API.

## Stop Condition

Stop if code changes would require widening S039 beyond flat face-normal Lambert or exposing backend
native material/light semantics.
