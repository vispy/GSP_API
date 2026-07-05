# ADR-0030 - MeshVisual Face Culling And Alpha Boundary

## Status

Accepted

## Context

S036 accepted static orthographic `View3D`, `(N,3)` `MeshVisual` rendering, and strict opaque-depth
capability gates. S044 accepted `query.view3d.mesh_triangle_pick.v1` for strict-scope opaque
DATA-space mesh triangles. S050 accepted unlit Texture2D materials but explicitly deferred culling,
non-opaque 3D alpha, alpha sorting, alpha test/discard, and transparent picking semantics.

P032 resolved the remaining S050 architecture question for the first face-culling boundary. This ADR
converts that response into protocol authority before any backend advertises strict culling support.

## Decision

GSP accepts strict face culling as a small, capability-gated v1 contract. Front/back classification
is defined in projected panel NDC, not in source/object coordinates, framebuffer coordinates,
backend screen coordinates, or backend default draw-state conventions.

For a source triangle `(i0, i1, i2)`, resolve panel-NDC vertices `q0`, `q1`, and `q2`. DATA-space
vertices are projected through the accepted `View3D` equations. NDC `(N,3)` vertices are interpreted
directly as panel NDC. The signed projected area is:

```text
area2 = (x1 - x0) * (y2 - y0) - (y1 - y0) * (x2 - x0)
```

`area2 > 0` is front-facing, `area2 < 0` is back-facing, and `area2 == 0` is projected-degenerate
and ambiguous. Front-facing therefore means counter-clockwise in panel NDC x/y. `z` does not
participate in winding classification.

`FaceCulling.BACK` suppresses triangles with `area2 < 0`. `FaceCulling.FRONT` suppresses triangles
with `area2 > 0`. Projected-degenerate triangles have no strict raster contribution and no strict
rendered-surface pick hit. Culling happens before depth test, depth write, order, adapted alpha
compositing, and query candidate selection.

Reversed `View3D.xlim` or `ylim` affect culling because they affect projected NDC. One reversed axis
flips winding; two reversed axes preserve it. Final framebuffer or y-down pixel mapping must not
flip the protocol result.

## Alpha Boundary

Strict non-opaque 3D alpha remains deferred. A 3D mesh is eligible for strict opaque depth only if
effective fragment alpha is provably `1.0` everywhere.

For unlit or flat-Lambert meshes, every resolved mesh color alpha must be exactly `1.0`. For
`texture2d_unlit`, strict opaque eligibility requires base alpha `1.0` everywhere and every texture
alpha byte equal to `255`.

Any effective alpha below `1.0` excludes the visual from:

```text
meshvisual.positions3d.opaque_depth.v1
query.view3d.mesh_triangle_pick.v1
strict 3D opaque-depth conformance fixtures
```

No strict backend-neutral alpha blend equation, transparent sorting, alpha test/discard,
alpha-to-coverage, depth peeling, weighted blended OIT, or transparent picking behavior is accepted
by this ADR. Adapted ordinary-alpha rendering may exist, but it is not a strict protocol feature.

## Capability Boundary

Accepted capability names:

```text
meshvisual.face_culling.data3d.projected_ndc.v1
meshvisual.face_culling.ndc3.panel_winding.v1
query.view3d.mesh_triangle_pick.face_culling.v1
```

`meshvisual.positions3d.opaque_depth.v1` remains restricted to fully opaque 3D meshes. Culling may
combine with strict opaque depth only when the relevant culling capability is also advertised. No
`meshvisual.alpha.blend.*.v1` capability is accepted here.

## Backend Expectations

Matplotlib may implement the canonical CPU projected-NDC winding calculation and filter faces before
building 2D polygon collections, but it remains an adapted 3D renderer unless fixtures prove the
claimed strict subset. It must not advertise strict opaque-depth support and must not treat ordinary
alpha as a blend contract.

Datoviz may advertise strict culling only after public APIs and fixtures demonstrate the accepted
projected-NDC winding behavior, reversed-bound behavior, culling before depth writes, and no leakage
from framebuffer y-down or native front-face conventions. Datoviz must not advertise culling-aware
mesh triangle picking until a public canonical face identity path exists.

VisPy2 may expose the protocol fields and lower them to GSP records, but it must not expose backend
handles or promise strict ordinary-alpha behavior.

## Deferred

Deferred after this ADR:

- strict non-opaque 3D alpha rendering;
- alpha blend equations and transparent sorting;
- alpha test/discard and OIT;
- strict transparent picking;
- strict clipping of partially clipped 3D triangles;
- mesh-local 3D transforms and transform-dependent culling;
- scene graphs, instancing, external model loading, and backend-native mesh handles;
- expanded 3D query payloads.

## Source

`.agent/consultations/P032-response.md` converted into this ADR and
`spec/visuals/mesh_face_culling_alpha_s050.md`.
