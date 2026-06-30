# S036 Next Stage Scoping - Static View3D and Orthographic 3D Mesh Baseline

## Decision

Open S036 from P020 as a small, static 3D stage.

## Scope

Accepted for S036:

- static `View3D`;
- camera-parameter-first public state: `eye`, `target`, `up`;
- orthographic projection with explicit x/y bounds and near/far distances;
- `(N, 3)` `MeshVisual` integration for `CoordinateSpace.DATA` and `CoordinateSpace.NDC`;
- opaque nearer-fragment-wins depth where strict capability is advertised;
- projection/ray query readback with snapshot coherence.

Deferred:

- public 3D navigation;
- perspective;
- matrix-first authoring;
- materials/lights/normals;
- scene graph/model transforms;
- transparency sorting;
- strict clipping of partially clipped triangles;
- 3D mesh picking.

## Mission Order

1. M154 - S036 View3D ADR/spec and validation baseline.
2. M155 - S036 projection and snapshot conformance.
3. M156 - S036 MeshVisual `(N, 3)` DATA/NDC rendering path.
4. M157 - S036 opaque depth fixture.
5. M158 - S036 query ray readback.
6. M159 - S036 review examples and adapted demo boundary.
7. M160 - S036 closeout and S037 recommendation.

## First Action

Start M154 locally. Do not launch external workers until the mission plan is approved and path locks
are checked.

