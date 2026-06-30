# S037 View3D Navigation and Datoviz Binding Decisions

Status: accepted by M162 from P021 response.

## Accepted

- S037 is `View3D` navigation plus Datoviz `View3D` binding, not a public
  material/light/texture stage.
- Public navigation is expressed as backend-neutral actions that produce new canonical `View3D`
  states.
- Canonical `View3D.camera` and `View3D.projection` remain the source of truth.
- Accepted navigation results increment `View3D.revision` and recompute the
  `View3DProjectionSnapshot`.
- Stale `base_view_revision`, stale `base_view_projection_snapshot_id`, and stale
  layout-dependent actions are rejected instead of silently rebased.
- Datoviz `View3D` support must be implemented through a private lowering layer from public GSP
  state; public API must not expose Datoviz camera, controller, draw-state, or material names.
- Datoviz must keep reporting `mesh3d_coordinate_space_unsupported` until retained `(N, 3)` DATA and
  NDC3 rendering are proven through public `View3D` semantics without z flattening.
- Matplotlib `(N, 3)` mesh rendering remains adapted: CPU projection to 2D plus far-to-near face
  sorting for opaque, non-intersecting triangles.
- Legacy Matplotlib projection/depth/culling/normal helper techniques may be reused internally.

## Capability-Gated

- `view3d.navigation.orbit_pan_zoom.v1`.
- Datoviz `view3d.static.orthographic.v1`.
- Datoviz `meshvisual.positions3d.data.view3d.v1`.
- Datoviz `meshvisual.positions3d.ndc.v1`.
- Datoviz `meshvisual.positions3d.opaque_depth.v1`.
- Datoviz `query.view3d.ray_readback.v1`.

## Deferred

Public materials, lights, textures, UV attributes, samplers, culling fields, 3D model matrices,
perspective projection, strict 3D clipping, strict 3D picking, and backend-native controller
exposure.

Future material/light/texture capability names are reserved only for later specs:

- `meshvisual.material.unlit_rgba.v1`
- `meshvisual.material.flat_lambert.v1`
- `meshvisual.material.flat_phong.v1`
- `view3d.light.ambient.v1`
- `view3d.light.directional.v1`
- `texture2d.rgba8.v1`
- `meshvisual.uv.vertex2d.v1`
- `meshvisual.material.texture2d_unlit.v1`

## Source

`.agent/consultations/P021-response.md` converted into ADR-0024 and
`spec/view3d_navigation.md`.
