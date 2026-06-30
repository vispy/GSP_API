# M157 - S036 opaque depth fixture

## Stage

S036 - Static View3D, Orthographic Projection, and 3D Mesh Baseline

## Status

Ready; depends on completed M156.

## Summary

Establish the minimal strict 3D depth contract for opaque meshes.

## Deliverables

- Opaque nearer-fragment-wins fixture with unambiguous overlapping triangles.
- No-face-culling fixture with reversed winding still visible.
- Alpha-less-than-one negative/adapted fixture.
- Clipping-edge behavior documented as adapted or unsupported unless strict clipping is implemented.

## Stop Condition

Stop if strict depth cannot be implemented or reported without exposing backend depth-buffer state as
public protocol.
