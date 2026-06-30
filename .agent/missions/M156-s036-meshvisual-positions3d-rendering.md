# M156 - S036 MeshVisual `(N, 3)` DATA/NDC rendering path

## Stage

S036 - Static View3D, Orthographic Projection, and 3D Mesh Baseline

## Status

Draft; depends on M155.

## Summary

Make `(N, 3)` `MeshVisual` renderable where a backend advertises the S036 3D capabilities.

## Deliverables

- `(N, 3)` DATA interpretation through `View3D`.
- `(N, 3)` NDC interpretation as panel NDC plus depth.
- Structured unsupported diagnostics for missing `View3D` or missing backend support.
- Datoviz retained rendering path if v0.4 bindings support it, otherwise a documented unsupported
  report with exact blocker evidence.
- Regression tests proving existing `(N, 2)` mesh behavior is unchanged.

## Stop Condition

Stop if Datoviz implementation requires public backend-native camera/draw-state names or if support
would silently flatten z.

