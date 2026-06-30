# S036 View3D Contract Decisions

Status: accepted by M154 from P020 response.

## Accepted

- S036 is a static 3D stage, not a public 3D navigation stage.
- Public camera state is `Camera3D(eye, target, up)`.
- Public projection is orthographic only.
- Public matrix-first authoring is deferred; derived matrices may appear later as diagnostics or
  snapshot readback.
- Existing `CoordinateSpace.DATA` and `CoordinateSpace.NDC` remain the only public visual coordinate
  spaces.
- `(N, 3)` DATA `MeshVisual` positions require compatible `View3D` support.
- `(N, 3)` NDC `MeshVisual` positions are interpreted as panel NDC x/y and GSP NDC depth.
- The only strict S036 depth contract is opaque nearer-fragment-wins where capability is advertised.
- S036 query/readback covers projection-inverse ray context, not 3D mesh picking.

## Capability-Gated

- Datoviz retained static orthographic `View3D` rendering.
- `(N, 3)` DATA and NDC mesh rendering.
- Opaque depth.
- Ray readback.

## Deferred

Public `View3DNavigationController`, perspective projection, public arbitrary view/projection
matrices, materials/lights/normals, scene graph/model transforms, instancing, external model loading,
transparency sorting, strict clipping of partially clipped triangles, 3D mesh picking, and non-mesh
3D visual families.

## Source

`.agent/consultations/P020-response.md` converted into ADR-0023 and `spec/view3d.md`.

