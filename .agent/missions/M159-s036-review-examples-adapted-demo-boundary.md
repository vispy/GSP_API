# M159 - S036 review examples and adapted demo boundary

## Stage

S036 - Static View3D, Orthographic Projection, and 3D Mesh Baseline

## Status

Ready; depends on completed M154-M158.

## Summary

Add user-facing examples that demonstrate useful static 3D behavior without promoting public 3D
navigation semantics.

## Deliverables

- Static cube mesh example.
- Simple terrain-like mesh example.
- NDC-depth triangle example.
- Opaque overlap/depth example.
- Alpha-not-strict negative/adapted example.
- Optional adapted interactive demo that emits canonical `View3D` replacements, clearly documented
  as non-public navigation semantics.

## Stop Condition

Stop if examples require public `View3DNavigationController`, perspective, materials/lights, or
backend-native controller objects.
