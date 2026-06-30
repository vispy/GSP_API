# ADR-0024 - View3D Navigation and Datoviz View3D Binding

## Status

Accepted

## Context

S036 accepted a static, orthographic, camera-parameter-first `View3D` baseline. It intentionally
deferred public 3D navigation, backend-native camera/controller exposure, perspective projection,
materials, lights, textures, strict 3D picking, and scene graph semantics.

P021 resolved the S037 direction after reviewing the completed S036 baseline, the Datoviz v0.4
unsupported boundary, and legacy Matplotlib 3D renderer code.

## Decision

S037 is a `View3D` navigation and Datoviz `View3D` binding stage.

Accepted for S037:

- public 3D navigation as backend-neutral actions over canonical `View3D` state;
- navigation results that produce new canonical `View3D.camera`, `View3D.projection`, revision, and
  projection snapshot identity;
- strict stale-revision and stale-snapshot rejection for navigation actions;
- a private Datoviz `View3D` lowering layer that accepts only public GSP `View3D` and `MeshVisual`
  state;
- Datoviz evidence gates before claiming any public `(N, 3)` `MeshVisual` support;
- Matplotlib 3D rendering remains explicitly adapted: CPU projection to 2D plus face sorting for
  opaque non-intersecting triangles;
- legacy projection, homogeneous transform, view/world-space helper math, NDC face-depth sorting,
  face normal, and screen-space winding utilities may be reused internally without public API
  changes.

Deferred from S037:

- public material, light, texture, UV, sampler, and culling fields;
- public perspective projection;
- public backend-native controllers, Datoviz cameras, Datoviz draw-state names, or Matplotlib
  artist/axes objects;
- strict 3D fragment-depth, clipping, transparency, and picking guarantees beyond accepted
  evidence gates;
- legacy public camera/material/light/texture class resurrection.

## Capability Boundary

S037 adds the navigation capability name:

```text
view3d.navigation.orbit_pan_zoom.v1
```

A backend supports this capability only when it accepts backend-neutral `View3DNavigationAction`
values for orbit, pan, zoom, reset, set-camera, and set-projection; validates base revisions and
snapshot ids; and returns a new canonical `View3D` state with a fresh revision and projection
snapshot.

Existing S036 capability names remain semantic and backend-neutral:

```text
view3d.static.orthographic.v1
meshvisual.positions3d.data.view3d.v1
meshvisual.positions3d.ndc.v1
meshvisual.positions3d.opaque_depth.v1
query.view3d.ray_readback.v1
```

Matplotlib may claim strict static projection, snapshot, and ray-readback behavior, but its `(N, 3)`
mesh raster output remains adapted unless a later strict fragment-depth contract is accepted.

Datoviz must continue returning `mesh3d_coordinate_space_unsupported` for public `(N, 3)`
`MeshVisual` until public `View3D` binding evidence proves DATA, NDC3, depth, snapshot, and query
semantics without silent z flattening.

## Consequences

S037 can open public 3D navigation without adopting a graphics-engine object model. The canonical
state remains `View3D`, not a backend controller.

Materials, lights, and textures become a later-stage design problem. Legacy Matplotlib Phong and
texture code may inform review-only experiments or future specs, but it is not capability evidence.

## Source

`.agent/consultations/P021-response.md` converted into this ADR,
`.agent/decisions/S037_view3d_navigation_datoviz_contracts.md`, and
`spec/view3d_navigation.md`.
