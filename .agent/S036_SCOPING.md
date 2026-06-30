# S036 Scoping - Static View3D, Orthographic Projection, and 3D Mesh Baseline

Status: completed. See `.agent/S036_CLOSEOUT.md`.

## Decision

Open S036 as the next implementation stage after S035 retained `View2D` navigation. The stage makes
`MeshVisual.positions` shaped `(N, 3)` useful through a small public `View3D` contract without adding
a general 3D engine object model.

This follows P020:

- static `View3D` only;
- camera represented as `eye`, `target`, and `up`;
- orthographic projection only;
- existing `CoordinateSpace.DATA` and `CoordinateSpace.NDC`;
- capability-gated `(N, 3)` `MeshVisual` rendering;
- opaque nearest-fragment depth semantics where strict support is claimed;
- strict projection/ray query readback;
- public `View3DNavigationController`, perspective, materials, lights, scene graph, and 3D picking deferred.

## Public Shape

S036 should add:

- `Camera3D`;
- `OrthographicProjection3D`;
- `View3D`;
- static projection helpers and validation diagnostics;
- capability names for static orthographic `View3D`, `(N, 3)` DATA/NDC mesh paths, opaque depth, and
  `View3D` ray readback;
- structured unsupported diagnostics for 3D mesh picking and unsupported backend capabilities.

## Mission Order

1. M154 - S036 View3D ADR/spec and validation baseline.
2. M155 - S036 projection and snapshot conformance.
3. M156 - S036 MeshVisual `(N, 3)` DATA/NDC rendering path.
4. M157 - S036 opaque depth fixture.
5. M158 - S036 query ray readback.
6. M159 - S036 review examples and adapted demo boundary.
7. M160 - S036 closeout and S037 recommendation.

## Stop Conditions

- Stop if implementation requires public perspective semantics.
- Stop if Datoviz requires exposing backend-native camera, material, draw-state, or controller
  objects as public protocol fields.
- Stop if strict 3D mesh picking is needed before the projection/ray readback contract is accepted.
- Stop if existing `(N, 2)` mesh or `View2D` behavior would regress.
