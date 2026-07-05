# P033 - 3D query payload expansion consultation

Use this as a single self-contained prompt for ChatGPT Pro.

```text
You are advising on GSP_API, a backend-neutral graphical scene protocol and Python producer API.
The project needs an architecture/spec decision for expanding 3D mesh query payloads beyond the
already accepted `query.view3d.mesh_triangle_pick.v1` result.

Please answer as an API/protocol architect, not as an implementation coder.

The response must be self-contained and must not assume access to files. Use the facts and excerpts
below as the complete project context.

Project context
===============

GSP_API defines formal protocol models for visual scenes. It has multiple backends:

- Matplotlib: reference/publication backend, correctness over speed, uses CPU/projection and
  Matplotlib artists.
- Datoviz v0.4: high-performance retained-scene GPU backend, but only public Datoviz APIs count as
  evidence. Private Vulkan state, shader slots, mesh ids, draw-state objects, framebuffer internals,
  and backend-native handles are not public GSP semantics.
- VisPy2: high-level Python producer API that emits GSP protocol records. It must not expose backend
  handles.

Authority order in the repo is:

1. PROJECT_CHARTER.md
2. ARCHITECTURE.md
3. SPEC_INDEX.md
4. spec/**
5. accepted ADRs and .agent/decisions/**
6. LEGACY_MAP.md
7. existing source code

Existing code is implementation material but not automatically authoritative. If code and spec
conflict, the spec wins.

Already accepted View3D facts
=============================

Accepted S036/S047 View3D baseline:

- `Camera3D`: finite `eye`, `target`, `up`.
- `OrthographicProjection3D`: explicit camera-plane `xlim`, `ylim`, `near_far`; reversed x/y bounds
  are valid; `near >= 0` and `far > near`.
- `PerspectiveProjection3D` exists as an accepted later direction, but most strict 3D mesh-pick work
  is still limited to orthographic `View3D`.
- `View3D`: 3D view attached to one panel.
- Orthographic projection maps DATA points into panel NDC3.
- `(N,3)` DATA mesh vertices are projected through `View3D`.
- `(N,3)` NDC mesh vertices are interpreted as panel NDC x/y/z.
- Panel NDC convention:
  - `x`: -1 left, +1 right
  - `y`: -1 bottom, +1 top
  - `z`: -1 near, +1 far
  - smaller z is closer
- Strict opaque depth is capability-gated as `meshvisual.positions3d.opaque_depth.v1`.
- Where strict opaque depth is claimed, nearer opaque fragment wins.
- Ray readback is separate: `query.view3d.ray_readback.v1`.
- 3D mesh triangle picking is accepted as `query.view3d.mesh_triangle_pick.v1` for strict-scope
  opaque DATA-space mesh triangles.

Accepted camera basis:

```text
forward = normalize(target - eye)
right   = normalize(cross(forward, up))
true_up = cross(right, forward)
```

Orthographic DATA-to-panel-NDC projection:

```text
p_rel = p - eye

camera_x = dot(p_rel, right)
camera_y = dot(p_rel, true_up)
camera_z = dot(p_rel, forward)

ndc_x = -1 + 2 * (camera_x - xlim[0]) / (xlim[1] - xlim[0])
ndc_y = -1 + 2 * (camera_y - ylim[0]) / (ylim[1] - ylim[0])
ndc_z = -1 + 2 * (camera_z - near) / (far - near)
```

Perspective projection is implemented in protocol helpers but expanded picking payload semantics for
perspective are not accepted yet.

Current MeshVisual protocol surface
===================================

The current `MeshVisual` dataclass shape is:

```python
class MeshVisual:
    id: str
    positions: FloatArray
    faces: IndexArray
    coordinate_space: CoordinateSpace
    color: ColorArray | None = None
    color_mode: MeshColorMode | None = None
    face_color_encoding: ScalarColorEncoding | None = None
    normal_mode: MeshNormalMode | None = None
    normals: FloatArray | None = None
    normal_generation: MeshNormalGeneration = MeshNormalGeneration.NONE
    shading: MeshShading = MeshShading.UNLIT_RGBA
    texture2d_id: str | None = None
    uv_mode: MeshUVMode = MeshUVMode.NONE
    uvs: FloatArray | None = None
    face_culling: FaceCulling = FaceCulling.NONE
    depth_test: DepthMode = DepthMode.AUTO
    depth_write: DepthMode = DepthMode.AUTO
    order: float = 0.0
    opacity_policy: OpacityPolicy = OpacityPolicy.ORDINARY_ALPHA
    transform: VisualTransformBinding | None = None
```

Current relevant enum shapes:

```text
MeshShading: unlit_rgba, flat_lambert, texture2d_unlit
FaceCulling: none, back, front
DepthMode: auto, enabled, disabled
OpacityPolicy: ordinary_alpha
CoordinateSpace: data, ndc, screen
```

Current accepted material facts:

- `meshvisual.material.unlit_rgba.v1`: output RGBA equals resolved base RGBA.
- `meshvisual.material.flat_lambert.v1`: accepted only for DATA-space 3D meshes with face normals
  and accepted simple lights.
- `meshvisual.material.texture2d_unlit.v1`: accepted for immutable RGBA8 `Texture2D`, per-vertex
  UVs, fixed nearest/clamp/no-mipmap sampling, and multiplicative unlit RGBA:

```text
output.rgb = clamp(base.rgb * tex.rgb, 0.0, 1.0)
output.a   = clamp(base.a * tex.a, 0.0, 1.0)
```

Strict opaque-depth and strict mesh-triangle-pick paths require effective alpha `1.0` everywhere.
For textured meshes, that requires base alpha `1.0` and every texture alpha byte `255`.

Accepted S044 mesh triangle pick v1
===================================

The accepted public capability is:

```text
query.view3d.mesh_triangle_pick.v1
```

Prerequisites:

```text
view3d.static.orthographic.v1
meshvisual.positions3d.data.view3d.v1
meshvisual.positions3d.opaque_depth.v1
```

Accepted v1 scope:

- orthographic `View3D`;
- `depth_mode="opaque_less"`;
- opaque, depth-writing, DATA-space `MeshVisual` triangle geometry;
- one panel point request;
- at most one result: frontmost visible supported triangle, miss, unsupported, stale, or invalid;
- public GSP visual ids and public canonical triangle indices only.

Current request shape:

```python
class View3DMeshTrianglePickRequest:
    view_id: str
    panel_xy: tuple[float, float]
    kind: str = "query.view3d.mesh_triangle_pick.v1"
    panel_id: str | None = None
    expected_layout_snapshot_id: str | None = None
    expected_view_revision: int | str | None = None
    expected_view_projection_snapshot_id: str | None = None
    expected_pick_scene_snapshot_id: str | None = None
```

Current response payload shape:

```python
class View3DMeshTrianglePickPayload:
    status: QueryStatus | str
    hit: bool
    view_id: str
    panel_xy: tuple[float, float]
    kind: str = "query.view3d.mesh_triangle_pick.v1"
    panel_id: str | None = None
    panel_ndc_xy: tuple[float, float] | None = None
    layout_snapshot_id: str | None = None
    view_revision: int | str | None = None
    view_projection_snapshot_id: str | None = None
    pick_scene_snapshot_id: str | None = None
    depth_mode: str | None = None
    visual_id: str | None = None
    visual_type: str | None = None
    primitive_kind: str | None = None
    primitive_index: int | None = None
    diagnostics: tuple[QueryDiagnostic, ...] = ()
```

For hit/miss, `panel_id`, `panel_ndc_xy`, `layout_snapshot_id`, `view_revision`,
`view_projection_snapshot_id`, `pick_scene_snapshot_id`, and `depth_mode="opaque_less"` are
required. For hits, `visual_id`, `visual_type="MeshVisual"`, `primitive_kind="triangle"`, and
`primitive_index` are required. Non-hit payloads must not include hit identity fields.

`primitive_index` is the public canonical `MeshVisual.faces` row for indexed triangle meshes. For
unindexed triangle-list meshes, it is the emitted triangle ordinal. If a backend cannot map its pick
result to this public index, it must not claim strict support.

`pick_scene_snapshot_id` is a backend-neutral freshness id for the depth-affecting public scene used
by the pick. It must change when eligible visual geometry, indices, visibility, depth mode, opacity
classification, layout, `View3D` revision, or projection state affecting the pick answer changes.

Current v1 deferred items include:

- NDC3 mesh picking;
- transparent meshes;
- non-mesh visuals;
- instancing;
- perspective projection;
- textures in query payloads;
- multi-hit selection;
- barycentric coordinates;
- interpolated DATA/world hit positions;
- normalized or raw depth values;
- ray distance;
- backend-native ids.

Accepted S050 culling boundary
==============================

P032 accepted strict face culling, but did not expand the v1 query payload.

For each source face `(i0, i1, i2)`, resolve panel-NDC vertices:

```text
q0 = (x0, y0, z0)
q1 = (x1, y1, z1)
q2 = (x2, y2, z2)
```

For DATA meshes, `qk = View3D.project(positions[ik])`. For NDC `(N,3)` meshes, `qk = positions[ik]`.
Signed projected area:

```text
area2 = (x1 - x0) * (y2 - y0) - (y1 - y0) * (x2 - x0)
```

Classification:

- `area2 > 0`: front-facing
- `area2 < 0`: back-facing
- `area2 == 0`: projected-degenerate / ambiguous

Accepted culling capabilities:

```text
meshvisual.face_culling.data3d.projected_ndc.v1
meshvisual.face_culling.ndc3.panel_winding.v1
query.view3d.mesh_triangle_pick.face_culling.v1
```

When `query.view3d.mesh_triangle_pick.face_culling.v1` is advertised, the strict candidate set
excludes culled and projected-degenerate triangles. Culled triangles behave as absent: they do not
occlude, do not win by depth, and must not be returned as hits.

The v1 query payload remains unchanged after P032. Backend-native mesh ids, Vulkan handles, private
Datoviz triangle ids, barycentrics, interpolated attributes, depth values, and `front_facing` fields
remain deferred to this separate 3D query-expansion track.

Current Datoviz evidence and blocker
====================================

Datoviz upstream API work is required before GSP can safely advertise
`query.view3d.mesh_triangle_pick.v1` for the Datoviz backend.

Local Datoviz v0.4 exposes public query plumbing:

- `DvzQueryResult`
- `DvzQueryRequest`
- `dvz_query_request`
- `dvz_panel_query`
- `dvz_panel_query_now`
- `dvz_scene_poll_query`
- `dvz_visual_id`
- `dvz_visual_set_query_capabilities`

`DvzQueryResult` fields include:

```text
freshness_serial
visual_id
visual_family
raw_target, raw_id
resolved_target, resolved_id
item_id
face_id
primitive_id
vertex_id
has_depth, depth
```

The public type vocabulary includes face/triangle identity fields, but current mesh query
implementation does not populate the face/triangle fields needed by GSP:

- mesh eligibility rejects request targets other than `NONE`, `ITEM`, or `OBJECT`;
- current mesh query geometry overwrites non-instanced per-primitive ids with `1u`;
- decoded non-instanced mesh hits therefore return `item_id = 0` for every triangle;
- instanced mesh ids represent instance ordinals, not triangle ordinals.

GSP currently keeps Datoviz mesh triangle picking unadvertised. The Datoviz protocol renderer
returns structured `unsupported` with diagnostic `pick.unsupported.no_public_primitive_map`.

Datoviz handoff requested that upstream Datoviz expose one of:

- `resolved_target = DVZ_SCENE_TARGET_TRIANGLE` with `resolved_id = <zero-based triangle row>`;
- `face_id = <zero-based face row>`;
- `primitive_id = <zero-based triangle row>`.

For indexed triangle meshes, the reported id must be the canonical public face row, not a source
vertex id, GPU draw vertex id, instance id, or backend-private primitive id.

Current Matplotlib reference behavior
=====================================

Matplotlib can provide a limited CPU reference oracle for strict-scope fixtures. Existing tests
verify:

- frontmost public triangle hit for two overlapping DATA-space triangles;
- background miss;
- outside-panel invalid;
- stale pick-scene snapshot;
- NDC3 mesh picking is currently unsupported by v1.

Matplotlib returns `pick.adapted.cpu_reference` for this path. It is a reference/adapted CPU oracle,
not proof that Matplotlib has strict GPU fragment-depth behavior.

Problem to solve
================

Design the next public 3D query payload boundary after S044/P032.

The project needs a decision for whether and how to add optional/query-versioned support for:

- barycentric coordinates;
- panel-NDC depth, camera-space depth, normalized depth, or raw backend depth;
- DATA-space hit position;
- panel-NDC hit position;
- ray parameter or camera-ray distance;
- front/back-facing or culling-state fields;
- per-hit normal, displayed RGBA, base color, scalar value, UV, texel, texture id, material id, or
  interpolated attributes;
- `hit_policy=all` / multi-hit results and ordering guarantees;
- vertex/edge picking;
- NDC3 mesh picking;
- perspective projection;
- transform interactions once mesh-local 3D transforms are accepted;
- instancing and model-loading hooks later;
- Datoviz-native fields without leaking private backend ids.

Please assume:

- The existing `query.view3d.mesh_triangle_pick.v1` should remain unchanged unless a strong reason
  exists to version or supersede it.
- Existing S044 hits must continue to identify only public `visual_id` and public canonical
  `primitive_index`.
- Expanded payloads must be capability-gated. Backends must be allowed to support v1 identity-only
  picking without supporting barycentrics, depth, attributes, multi-hit, or vertex/edge picking.
- Datoviz current blocker means GSP must not design around private native implementation details.
- P032 culling is accepted, but culling-aware picking is separate from expanded payload fields.
- Strict non-opaque 3D alpha and transparent picking are still deferred.

Questions to answer
===================

1. Should expanded 3D query payloads be added as optional fields on
   `query.view3d.mesh_triangle_pick.v1`, or as a new version/capability such as
   `query.view3d.mesh_triangle_pick.rich.v1` or `query.view3d.mesh_triangle_pick.v2`?

2. Which payload fields should be accepted now for a strict, backend-neutral v1 expansion? For each
   accepted field, specify:
   - name;
   - type and units;
   - coordinate space;
   - required/optional status;
   - validity prerequisites;
   - numerical tolerance expectations;
   - whether it is per-hit, per-request, or per-visual metadata.

3. Which fields should remain deferred, and why?

4. How should barycentric coordinates be defined?
   - relative to source face vertex order?
   - in projected panel-NDC screen space or in 3D DATA/ray intersection space?
   - what are edge/vertex tolerance rules?
   - how should partially clipped triangles be handled?

5. How should depth be represented, if at all?
   - panel NDC z in `[-1, 1]` with smaller closer?
   - camera-space depth?
   - normalized depth buffer value?
   - ray distance?
   - multiple depth fields with distinct capability names?

6. Should `DATA` hit position be accepted now?
   - For orthographic only?
   - For perspective only after perspective pick is accepted?
   - Computed from triangle/ray intersection or barycentric interpolation?
   - How should backend floating-point tolerance be bounded?

7. Should UV/texel/material/color/readback fields be accepted now for textured meshes, or deferred
   until Datoviz Texture2D renderer support and strict sampling evidence exist?

8. Should `hit_policy=all` / multi-hit 3D picking be accepted now?
   - If yes, define ordering, occlusion, culling, depth ties, duplicate suppression, maximum result
     behavior, and payload shape.
   - If no, define the future capability boundary.

9. Should vertex/edge picking be part of this expansion, or separate capabilities?
   - How should tolerance and ambiguity be specified?
   - Should vertex/edge ids be source mesh indices, emitted primitive ordinals, or something else?

10. How should the expansion interact with accepted P032 culling?
    - Should returned hits include `front_facing`, `culled`, or `culling_state`?
    - Should these fields be required only when
      `query.view3d.mesh_triangle_pick.face_culling.v1` is advertised?

11. How should perspective projection, mesh-local transforms, instancing, and external model loading
    be handled in the design?

12. What capability names and diagnostics should GSP add?

13. What minimal conformance fixtures should be required before any backend advertises the expanded
    query capability?

14. What Datoviz upstream API evidence would be sufficient for each accepted field, given current
    public fields like `face_id`, `primitive_id`, `has_depth`, and `depth`?

Expected output format
======================

Please answer with exactly these sections:

1. Executive Decision
   - State whether to keep v1 unchanged and add optional capability payloads, or create a new
     version/capability.

2. Accepted Payload Boundary
   - A table of accepted fields with name, type, units, coordinate space, prerequisites, and
     capability name.

3. Deferred Payloads
   - A table of deferred fields/features with reason and future trigger.

4. Barycentric Semantics
   - Exact definition and edge/vertex/tolerance policy.

5. Depth And Hit Position Semantics
   - Exact depth and position fields to accept or defer.

6. Multi-Hit / Hit Policy Decision
   - Whether to accept now; if deferred, give future capability names and blockers.

7. Vertex/Edge Picking Decision
   - Whether to accept now; if deferred, give future capability names and blockers.

8. Culling / Alpha / Texture Interaction
   - How P032 culling and strict opaque-alpha boundaries affect expanded payloads.

9. Perspective / Transform / Instancing Boundary
   - What is accepted now and what is explicitly deferred.

10. Capability Names And Diagnostics
    - List precise capability strings and diagnostic strings.

11. Fixture Plan
    - Minimal positive and negative fixtures before backend advertisement.

12. Datoviz Evidence Requirements
    - Public Datoviz fields/APIs/tests needed for each accepted capability.

13. Implementation Plan
    - Ordered, conservative GSP missions after this consultation.

14. Risks / Non-Goals
    - Overclaiming risks and non-goals.
```
