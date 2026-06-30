# M155 - S036 projection and snapshot conformance

## Stage

S036 - Static View3D, Orthographic Projection, and 3D Mesh Baseline

## Status

Draft; depends on M154.

## Summary

Implement backend-independent orthographic projection math and snapshot identity for `View3D`.

## Deliverables

- Deterministic camera basis derivation.
- DATA-to-camera and camera-to-NDC projection helpers.
- View/projection snapshot identity fields.
- Numeric fixtures for canonical basis, cube projection, reversed x/y bounds, and off-axis bounds.
- Tests proving projection math is independent of raster backend.

## Stop Condition

Stop if projection conventions are ambiguous or if a backend-specific clip/depth convention leaks into
the public protocol.

