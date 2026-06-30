# M158 - S036 query ray readback

## Stage

S036 - Static View3D, Orthographic Projection, and 3D Mesh Baseline

## Status

Draft; depends on M155.

## Summary

Add strict `View3D` projection-inverse query context while keeping 3D visual picking deferred.

## Deliverables

- Query payload for panel logical xy, panel NDC xy, near/far DATA points, ray direction, view id,
  view revision, layout snapshot id, and view/projection snapshot id.
- Center and corner ray fixtures.
- Stale snapshot mismatch diagnostics.
- Structured unsupported result for 3D mesh hit/picking requests.

## Stop Condition

Stop if the query model starts requiring ray-triangle picking, depth-buffer readback, barycentric
attributes, or multi-hit stack semantics.

