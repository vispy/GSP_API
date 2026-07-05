# View3D Mesh Triangle Picking

Status: accepted S044 protocol boundary.

Semantic purpose: define the first backend-neutral 3D visual-hit query without exposing backend GPU,
framebuffer, shader, controller, or object-id internals.

## Capability

Strict support is advertised by:

```text
query.view3d.mesh_triangle_pick.v1
```

Prerequisites:

```text
view3d.static.orthographic.v1
meshvisual.positions3d.data.view3d.v1
meshvisual.positions3d.opaque_depth.v1
```

`query.view3d.ray_readback.v1` shares panel coordinate and snapshot conventions, but it is a
camera/layout ray-context query and does not imply mesh-triangle picking.

## Scope

Accepted v1 scope:

- orthographic `View3D`;
- `depth_mode="opaque_less"`;
- opaque, depth-writing, DATA-space `MeshVisual` triangle geometry;
- one panel point request;
- at most one result: frontmost visible supported triangle, miss, unsupported, stale, or invalid;
- public GSP visual ids and public canonical triangle indices only.

Deferred: NDC3 mesh picking, transparent meshes, non-mesh visuals, instancing, perspective
projection, textures, multi-hit selection, barycentric coordinates, interpolated DATA/world hit
positions, depth values, ray distance, and backend-native ids. S050 accepts culling-aware picking
only as a separate additive capability, `query.view3d.mesh_triangle_pick.face_culling.v1`.

## Request

`request.kind` must be `query.view3d.mesh_triangle_pick.v1`.

Required fields:

- `view_id`: public `View3D.id`;
- `panel_xy`: query point in the same public panel coordinate convention used by
  `query.view3d.ray_readback.v1`.

Optional guards:

- `panel_id`: if supplied, mismatch with the resolved `View3D.panel_id` returns `invalid`;
- `expected_layout_snapshot_id`: mismatch returns `stale`;
- `expected_view_revision`: mismatch returns `stale`;
- `expected_view_projection_snapshot_id`: mismatch returns `stale`;
- `expected_pick_scene_snapshot_id`: mismatch returns `stale`.

## Response

`response.kind` must be `query.view3d.mesh_triangle_pick.v1`.

Required fields:

- `status`: `hit | miss | unsupported | stale | invalid`;
- `hit`: true only for `status == "hit"`;
- `view_id`;
- `panel_id` when resolvable;
- `panel_xy`;
- `panel_ndc_xy` for hit/miss;
- `layout_snapshot_id` for hit/miss;
- `view_revision` for hit/miss;
- `view_projection_snapshot_id` for hit/miss;
- `pick_scene_snapshot_id` for hit/miss;
- `depth_mode="opaque_less"` for hit/miss;
- `visual_id` for hit, otherwise null;
- `visual_type="MeshVisual"` for hit, otherwise null;
- `primitive_kind="triangle"` for hit, otherwise null;
- `primitive_index` for hit, otherwise null;
- `diagnostics`: stable backend-neutral diagnostic entries.

`primitive_index` is the public canonical `MeshVisual` triangle stream index. For indexed triangle
faces, it is the row index in the public face array. For unindexed triangle lists, it is the emitted
triangle ordinal. If a backend cannot map its pick result to this public index, it must not claim
strict support.

`pick_scene_snapshot_id` is a backend-neutral freshness id for the depth-affecting public scene used
by the pick. It must change when eligible visual geometry, indices, visibility, depth mode, opacity
classification, layout, `View3D` revision, or projection state affecting the pick answer changes.

## Strict Semantics

"Frontmost visible hit" means the supported `MeshVisual` triangle fragment at the query sample that
would win the public opaque depth test for the reported layout, `View3D`, projection snapshot, and
pick-scene snapshot.

For v1, smaller projected depth wins under `opaque_less`. A miss means no supported opaque
DATA-space `MeshVisual` triangle covers the query sample after applying v1 viewport, clipping, and
depth semantics.

When `query.view3d.mesh_triangle_pick.face_culling.v1` is advertised, the candidate set also
excludes triangles culled by `MeshVisual.face_culling` under the projected-NDC rules in
`spec/visuals/mesh_face_culling_alpha_s050.md`. Culled triangles and projected-degenerate triangles
behave as absent: they do not occlude, do not win by depth, and must not be returned as hits. The
response payload is unchanged and still returns only public GSP visual id plus canonical public
triangle index.

Triangle edge/vertex and exact depth-tie cases are intentionally not cross-backend deterministic in
v1. Backends may report ambiguity diagnostics for those cases, and conformance fixtures should avoid
them except for explicit ambiguity tests.

## Diagnostics

Stable diagnostic codes include:

- `pick.unsupported.backend`;
- `pick.unsupported.projection`;
- `pick.unsupported.depth_mode`;
- `pick.unsupported.coordinate_space`;
- `pick.unsupported.visual_type`;
- `pick.unsupported.transparent`;
- `pick.unsupported.instancing`;
- `pick.unsupported.non_triangle_mesh`;
- `pick.unsupported.no_public_primitive_map`;
- `pick.unsupported.scene_occluder`;
- `pick.unsupported.native_state_only`;
- `query_3d_mesh_culling_unsupported`;
- `pick.stale.layout_snapshot`;
- `pick.stale.view_revision`;
- `pick.stale.view_projection_snapshot`;
- `pick.stale.pick_scene_snapshot`;
- `pick.invalid.view_id`;
- `pick.invalid.panel_id`;
- `pick.invalid.panel_point`;
- `pick.invalid.outside_panel`;
- `pick.adapted.cpu_reference`;
- `pick.adapted.rasterization_tolerance`;
- `pick.ambiguous.edge_or_vertex`;
- `pick.ambiguous.depth_tie`.

## Backend Behavior

Matplotlib may provide a limited CPU reference oracle for eligible fixtures by projecting public
DATA-space triangles through public `View3D` state and applying public viewport, near/far, and
opaque-depth rules. It should include `pick.adapted.cpu_reference` unless and until strict
conformance is proven.

Datoviz may use an offscreen integer-id/depth picking pass, shader storage, color-id readback, or
another private strategy. Returned ids must be public GSP ids and public triangle indices. Pick
state must be invalidated by retained navigation, layout changes, mesh buffer/index changes,
visibility changes, opacity classification changes, and depth-mode changes.

Older or unsupported builds must return structured unsupported, stale, or invalid results. They must
not encode unsupported states as misses.

## Required Fixtures

Before strict advertisement, fixtures must cover single-triangle hits, background miss, outside
panel invalid, multi-visual selection, overlapping depth selection, same-visual occlusion,
near/far clipping, panel-to-NDC conversion, navigation updates without mesh reupload, stale snapshot
guards, indexed and unindexed primitive mapping, multi-panel routing, unsupported projection,
unsupported coordinate space, transparent mesh unsupported, unsupported scene occluders, ambiguity
at edges/vertices, equal-depth ties, and absence of backend-native ids in payloads.
