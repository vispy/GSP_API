# S027 Transform/View Contract Decisions

Status: accepted by M099 from P012 response.

## Accepted

- S027 is a 2D-first transform, view, and query-inverse stage.
- Public v1 defines only finite invertible `AFFINE_2D` transforms, either as named resources or
  small inline visual transform bindings.
- `CoordinateSpace.NDC` and `CoordinateSpace.DATA` remain the only accepted public visual coordinate
  spaces.
- A visual-local affine transform is applied to positional geometry before interpreting coordinates
  in the visual's declared coordinate space.
- `View2D` is deterministic panel-level state with finite linear `xlim` and `ylim`; pan and zoom are
  represented as explicit `View2D` updates.
- Query inverse/readout is part of S027. Strict transformed query results report panel coordinates,
  declared-space coordinates, source/local coordinates when invertible, data coordinates for DATA
  visuals, transform identity, inverse status, and diagnostics.
- Semantic guides derive ticks, grids, labels, and data readouts from `View2D`.
- Matplotlib is the strict reference backend for the accepted 2D subset.

## Capability-Gated

- Datoviz may use native GPU placement or explicit CPU adaptation for finite eager arrays, but
  placement/adaptation must be reported.
- Transform query inverse is advertised separately from render support.
- 2D mesh-local transforms are accepted for strict flat triangle meshes; broader depth and camera
  behavior is not.

## Deferred

Public 3D camera/view/projection semantics, controller/navigation event state, transform stacks or
graphs, nonlinear/log/geospatial/category transforms, equal-aspect layout semantics, arbitrary image
rotation/skew, texture-coordinate transforms, depth ordering, 3D mesh query, source/virtual-data
transforms, backend-native transform objects, shader/material transforms, layout engines, and hidden
CPU materialization of virtual or huge sources.

## Source

`.agent/consultations/P012-response.md` converted into ADR-0019 and `spec/transforms.md`.
