# ADR-0019 - Transform, View, and Query Inverse v1

## Status

Accepted

## Context

S027 follows the accepted visual-family, text, mesh, and color-mapping baselines. The project needs
transform and view semantics before adding broader navigation, camera, or backend placement behavior.
This area is risky because Matplotlib, Datoviz, and future VisPy2 APIs all expose different native
transform concepts, and importing any one of those object models into public GSP would make replay,
query/readback, and cross-backend conformance fragile.

Query/readback is first-class in GSP. Any transform baseline must therefore define inverse coordinate
reporting, not just rendered output.

## Decision

S027 accepts a narrow 2D protocol baseline:

- Public transforms are GSP protocol resources or inline records, not backend-native objects.
- The only accepted transform kind is finite invertible `AFFINE_2D`, serialized as a row-major
  homogeneous 3x3 matrix with final row `[0, 0, 1]` and non-zero 2x2 determinant.
- `CoordinateSpace.DATA` and `CoordinateSpace.NDC` remain the only accepted public visual coordinate
  spaces in S027. Local/model/world/screen/camera names may appear as explanatory stages or query
  fields, but not as new public visual coordinate-space enum values.
- A visual may carry at most one visual-local/model affine transform binding. It applies to
  positional geometry before the result is interpreted in the visual's declared coordinate space.
- `View2D` is panel-level deterministic state. It maps DATA x/y values to panel NDC with explicit
  linear `xlim` and `ylim`. Reversed limits are allowed; zero-width, non-finite, log, nonlinear, and
  equal-aspect layout semantics are not accepted in S027.
- Pan and zoom are represented as explicit `View2D` updates. Public controller, gesture, interaction,
  inertia, linked-navigation, and event semantics are deferred.
- Query inverse/readout is required for strict S027 support. Transformed query payloads report panel
  coordinates, panel NDC, declared-space coordinates, source/local coordinates where invertible, data
  coordinates for DATA visuals, transform ids, and inverse status/diagnostics.
- Semantic guides consume `View2D` for ticks, grids, labels, and data readouts. Layout, collision
  solving, margins, and publication styling remain backend/layout policy.
- Public 3D camera, `View3D`, projection, depth, clipping-plane, orbit-controller, 3D mesh query,
  material, lighting, and perspective semantics are reserved but deferred.
- Capability records must distinguish semantic support from placement. Placement may be native GPU,
  CPU adapter, server-side, client-side, mixed, or unsupported, but it must not change accepted
  semantics except within declared tolerances.

## Consequences

Workers can implement S027 incrementally without freezing a broad graphics-engine transform graph.
The next implementation missions should add protocol dataclasses/enums/validation, Matplotlib strict
render/query behavior, Datoviz capability gates and explicit adaptation reports, VisPy2 producer
conveniences, and deterministic visual/query fixtures.

Backends must reject unsupported public 3D, nonlinear, image-affine, virtual-source materialization,
or controller semantics with structured diagnostics instead of silently adapting them. If existing
source code conflicts with this ADR or `spec/transforms.md`, workers must stop and report the
conflict rather than inventing a third behavior.
