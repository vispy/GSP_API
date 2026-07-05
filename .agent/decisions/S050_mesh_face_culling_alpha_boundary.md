# S050 Mesh Face Culling And Alpha Boundary

Status: accepted from P032 response.

Authority:

- `adr/ADR-0030-mesh-face-culling-alpha-boundary.md`
- `spec/visuals/mesh_face_culling_alpha_s050.md`
- `.agent/consultations/P032-response.md`

## Decision

Accept strict `MeshVisual.face_culling` only as projected panel-NDC semantics:

- DATA `(N,3)` triangles are classified after accepted `View3D` projection;
- NDC `(N,3)` triangles are classified directly in panel NDC;
- front-facing means `area2 > 0`, counter-clockwise in panel NDC x/y;
- reversed `xlim` or `ylim` affect winding through projection;
- framebuffer y-down or backend-native front-face conventions are not protocol authority;
- culled and projected-degenerate triangles do not render, write depth, occlude, or participate in
  strict mesh-triangle picking.

Accepted capabilities:

```text
meshvisual.face_culling.data3d.projected_ndc.v1
meshvisual.face_culling.ndc3.panel_winding.v1
query.view3d.mesh_triangle_pick.face_culling.v1
```

## Alpha Boundary

Strict non-opaque 3D alpha remains deferred. Strict opaque-depth and strict 3D triangle-pick paths
require effective alpha `1.0` everywhere. For `texture2d_unlit`, that means base alpha `1.0`
everywhere and every texture alpha byte equal to `255`.

No strict alpha blending, transparency sorting, alpha test/discard, OIT, or transparent picking
capability is accepted.

## Implementation Gate

Do not advertise strict culling until fixtures prove projected-NDC winding, reversed-bound behavior,
framebuffer-y independence, and culling before depth. Do not advertise culling-aware picking until
the query path applies the same culling rule and can return canonical public face identity.

Matplotlib may be a CPU reference/adapted path, but it must not imply strict opaque depth. Datoviz
requires public runtime evidence before capability promotion. VisPy2 may expose protocol fields
without backend-native handles or strict ordinary-alpha claims.

## Still Deferred

Strict transparent 3D rendering, blend equations, transparent sorting, alpha test/discard, OIT,
strict transparent picking, strict clipping of partially clipped 3D triangles, mesh-local 3D
transforms, scene graphs, instancing, external model loading, backend-native handles, and expanded
3D query payloads remain separate architecture tracks.
