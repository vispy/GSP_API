# S050 strict 3D depth and mesh semantics scoping

## Mission

M203 - S050 strict 3D depth and mesh semantics scoping.

## Authority reviewed

- `PROJECT_CHARTER.md`
- `ARCHITECTURE.md`
- `SPEC_INDEX.md`
- `spec/view3d.md`
- `spec/view3d_mesh_triangle_picking.md`
- `.agent/S036_CLOSEOUT.md`
- `.agent/S040_CLOSEOUT.md`
- `.agent/S044_SCOPING.md`
- `.agent/S046_CLOSEOUT.md`
- `.agent/S047_CLOSEOUT.md`
- `.agent/S050_DATOVIZ_MESH_PICK_EVIDENCE.md`

## Current facts

`meshvisual.positions3d.opaque_depth.v1` remains a strict capability boundary. The View3D spec
requires that, for strict opaque depth, the nearer opaque fragment wins where the capability is
claimed. The current repository does not contain independent runtime evidence that either backend
meets that strict fragment-depth rule.

The Matplotlib backend still uses a projected 2D polygon path for 3D mesh raster output. It orders
faces with CPU depth sorting, which is useful as an adapted rendering path and for protocol-level
fixtures, but it is not strict GPU or fragment-depth evidence.

The Datoviz backend has a retained View3D DATA-space path that can enable native depth test/write
state when retained View3D support is available. That is necessary implementation plumbing, but it is
not sufficient evidence for advertising strict opaque depth. S050 also found current Datoviz
offscreen review instability in the colorbar path, so any Datoviz runtime proof should be bounded and
should stop cleanly on runtime crashes.

S050 M200/M205 found that Datoviz mesh query results do not yet expose canonical mesh face or
triangle identity. That blocks `query.view3d.mesh_triangle_pick.v1` promotion independently from
strict opaque depth. A strict depth proof should therefore not be coupled to native Datoviz
mesh-picking promotion.

`MeshVisual` already exposes `face_culling`, `depth_test`, `depth_write`, and ordinary alpha policy
surface area. The specs reviewed here do not yet define strict culling semantics, transparent 3D mesh
semantics, barycentric query payloads, depth-value readback, multi-hit picking, or vertex-query
expansion.

## Decisions

- Do not advertise `meshvisual.positions3d.opaque_depth.v1` for Datoviz until a strict less-depth
  runtime proof exists for retained DATA-space View3D mesh rendering.
- Keep Matplotlib's 3D mesh raster behavior documented as adapted. It can remain a CPU reference for
  projection and triangle-pick fixtures, but not a strict opaque-depth backend.
- Keep non-opaque alpha rejected for strict 3D mesh paths. There is no accepted alpha-blending or
  order-independent-transparency contract.
- Treat culling as protocol surface area without strict accepted semantics until a spec/ADR defines
  winding, front-face convention, interaction with transforms, and query behavior.
- Keep face/vertex query expansion out of implementation work until a consultation or accepted spec
  defines payload shape and capability names.

## Follow-up missions

- M209: local strict opaque-depth fixture plan. This should design minimal fixtures and acceptance
  criteria without promoting any backend capability.
- M210: Datoviz retained View3D depth runtime proof. This should run only after a stable bounded
  offscreen path is available, and should stop on Datoviz runtime crashes.
- M211: culling and alpha semantics consultation packet. This is an API/spec decision and needs
  ChatGPT Pro before implementation.
- M212: 3D query payload expansion consultation packet. This covers barycentrics, depth values,
  multi-hit payloads, and vertex/edge expansion beyond S044 v1.
