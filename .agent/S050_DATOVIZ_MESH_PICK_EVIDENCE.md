# S050 Datoviz Native Mesh-Pick Evidence

Date: 2026-07-03

Mission: M200 - S050 Datoviz native mesh-pick evidence spike

## Conclusion

Datoviz upstream API work is required before GSP can safely advertise
`query.view3d.mesh_triangle_pick.v1` for the Datoviz backend.

The local Datoviz v0.4 checkout exposes enough public query plumbing for ordinary panel query
execution and result decoding, and it exposes a public native visual id. It does not currently
populate a public face/triangle/primitive id for mesh query hits. The current native mesh query path
returns only an item id, and for ordinary non-instanced meshes that item id is forced to `0` after
decode. GSP therefore cannot map a native mesh query hit to the public canonical
`MeshVisual.faces` row required by S044.

No Datoviz capability was promoted. No public GSP protocol semantics were changed.

## GSP Boundary Audited

Authoritative S044 boundary:

- `spec/view3d_mesh_triangle_picking.md`
- `adr/ADR-0028-view3d-mesh-triangle-picking.md`
- `.agent/decisions/S044_view3d_mesh_triangle_picking.md`

Strict Datoviz support requires all of:

- public GSP `visual_id`;
- public canonical triangle `primitive_index`;
- hit/miss freshness against layout snapshot, `View3D.revision`, projection snapshot, and
  pick-scene snapshot;
- structured `unsupported`, `stale`, or `invalid` results instead of silent misses.

Current GSP Datoviz adapter behavior is conservative and correct:

- `src/gsp_datoviz/capabilities.py` advertises `query.view3d.ray_readback.v1` when View3D camera
  bindings are ready, but explicitly does not add
  `QUERY_VIEW3D_MESH_TRIANGLE_PICK_CAPABILITY`.
- The same file records `s044_mesh_triangle_pick_diagnostics` with
  `pick.unsupported.no_public_primitive_map` and `pick.unsupported.native_state_only`.
- `DatovizV04ProtocolRenderer.query_view3d_mesh_triangle_pick()` returns structured
  `QueryStatus.UNSUPPORTED` with
  `View3DMeshPickDiagnosticCode.UNSUPPORTED_NO_PUBLIC_PRIMITIVE_MAP`.
- `tests/test_datoviz_v04_protocol_renderer.py` asserts that Datoviz does not advertise the S044
  capability and that the query returns structured unsupported.

## Datoviz Checkout

Read-only sibling checkout inspected:

- path: `/home/cyrille/GIT/Viz/datoviz`
- branch: `v0.4-dev`
- commit: `dc8b168ed86e0f674be204d00c29e5869ee5e6c4`
- pre-existing dirty file: `NOTES`

No Datoviz files were edited.

## Public Runtime Symbols

With `PYTHONPATH=/home/cyrille/GIT/Viz/datoviz`, the local Python facade exposes:

- `DvzQueryResult`
- `DvzQueryRequest`
- `dvz_query_request`
- `dvz_panel_query`
- `dvz_panel_query_now`
- `dvz_scene_poll_query`
- `dvz_visual_id`
- `dvz_visual_set_query_capabilities`

`DvzQueryResult._fields_` includes candidate identity fields:

- `freshness_serial`
- `visual_id`
- `visual_family`
- `raw_target`, `raw_id`
- `resolved_target`, `resolved_id`
- `item_id`
- `face_id`
- `primitive_id`
- `vertex_id`
- `has_depth`, `depth`

These fields are exposed, but the mesh query implementation does not populate the face/triangle
fields needed by S044.

## Source Evidence

### Query Result Shape

`include/datoviz/scene/types.h` defines:

- `DvzQueryRequest` with `target`, `hit_policy`, and `profile`;
- `DvzQueryResult` with `freshness_serial`, `visual_id`, `item_id`, `face_id`,
  `primitive_id`, `has_depth`, and `depth`.

`include/datoviz/scene/enums.h` defines:

- `DVZ_SCENE_TARGET_FACE`
- `DVZ_SCENE_TARGET_TRIANGLE`
- `DVZ_QUERY_CAPABILITY_FACE`

So the public type vocabulary has room for face/triangle identity, but the current mesh query path
does not implement that target.

### Public Visual Identity

`include/datoviz/scene.h` exposes `dvz_visual_id(const DvzVisual* visual)`.

`src/scene/visuals/families.c` implements `_scene_visual_public_id()` by returning `visual->id`
when the visual belongs to the scene.

`src/scene/query/result.c` sets `out_result->visual_id =
_scene_visual_public_id(ctx->build->figure->scene, visual)` in
`_dvz_scene_query_decode_item_id()`.

This is enough native evidence for a GSP-side map from Datoviz visual id to GSP `visual.id`, if GSP
records the `dvz_visual_id()` value at visual creation time.

### Mesh Query Identity

`src/scene/visuals/mesh/query.c`:

- uses `_dvz_scene_query_item_target_eligible(visual, request, DVZ_VISUAL_TYPE_MESH)`;
- builds a `DVZ_FORMAT_R32_UINT` query render target;
- calls `_scene_query_mesh_item_geometry()`;
- decodes with `_dvz_scene_query_decode_item_id(ctx, DVZ_SCENE_VISUAL_FAMILY_MESH, out_result)`;
- leaves `_mesh_query_readout()` as `value_kind = DVZ_QUERY_VALUE_NONE`.

`src/scene/query/policy.c` maps `DVZ_SCENE_TARGET_FACE` and
`DVZ_SCENE_TARGET_TRIANGLE` to `DVZ_QUERY_CAPABILITY_FACE`, but
`_dvz_scene_query_item_target_eligible()` rejects any request target other than
`NONE`, `ITEM`, or `OBJECT`.

Therefore the mesh family path currently does not accept native face or triangle query targets.

`src/scene/visuals/query_geometry.c` is decisive:

- `_scene_query_indexed_primitive_geometry()` can derive a per-primitive encoded id:
  `scratch->query_ids[dst] = (uint32_t)prim + 1u`.
- `_scene_query_mesh_item_geometry()` calls that helper and then, when no
  `instance_transform` attribute exists, overwrites every query id with `1u`.
- After `_dvz_scene_query_decode_item_id()`, that becomes `item_id = 0` for every non-instanced
  mesh hit.
- When `instance_transform` exists, ids become instance ordinals, not triangle ordinals.

This means current native mesh query results cannot identify the winning canonical triangle.

### Query Freshness

Datoviz has request/result freshness, but not the S044 pick-scene snapshot required by GSP:

- `DvzQueryResult.freshness_serial` exists.
- `src/scene/core/scene.c` allocates monotonic request serials with `_scene_next_request_serial()`.
- `src/scene/query/queue.c` assigns `pending->freshness_serial` and tracks latest request serials.
- `src/scene/query/result.c` drops superseded results for the same request scope.

This is useful for stale queued-result suppression. It is not a backend-neutral
`pick_scene_snapshot_id` that changes when eligible mesh geometry, indices, visibility, depth mode,
opacity classification, layout, `View3D` revision, or projection state changes.

GSP could compute its own pick-scene snapshot from public GSP state, but it still needs native
triangle identity before that snapshot can validate a native pick answer.

### View3D/Layout Matching

The existing GSP Datoviz adapter already computes canonical `View3DProjectionSnapshot` ids from
public `View3D` state and `layout_snapshot_id`. It also stores retained View3D mesh attachments in
`retained_view3d_meshes`, but those attachments currently record only:

- `visual_id`
- `native_visual`

They do not include native query-capability state or a native primitive map because the current
Datoviz mesh query result does not expose the needed triangle id.

## Viability Assessment

| Requirement | Evidence | Result |
|---|---|---|
| Native panel query queue/poll | `dvz_panel_query`, `dvz_panel_query_now`, `dvz_scene_poll_query` | Present |
| Decodable result struct | `DvzQueryResult._fields_` exposed in Python | Present |
| Public native visual id | `dvz_visual_id`, `DvzQueryResult.visual_id` | Present |
| GSP visual id mapping | GSP can store `dvz_visual_id()` beside `visual.id` | GSP-only feasible |
| Canonical triangle id | Mesh query overwrites non-instanced ids to one item id | Missing |
| Native face/triangle target | enum/capability names exist, mesh eligibility rejects them | Missing |
| Depth/frontmost query render | mesh query uses render target and native depth state metadata | Partially present, still fixture needed |
| Pick-scene freshness id | Datoviz has request freshness, not scene semantic snapshot | GSP-side possible after triangle id exists |

Outcome: not viable as a GSP-only implementation.

## Required Datoviz Upstream API Evidence

A future Datoviz handoff should request one of the following public, tested behaviors:

1. Mesh query accepts `DVZ_SCENE_TARGET_FACE` or `DVZ_SCENE_TARGET_TRIANGLE` when the visual declares
   `DVZ_QUERY_CAPABILITY_FACE`.
2. Mesh query hits populate at least one of `DvzQueryResult.face_id`,
   `DvzQueryResult.primitive_id`, or `resolved_target=DVZ_SCENE_TARGET_TRIANGLE` plus
   `resolved_id`.
3. For indexed triangle meshes, the reported id is the canonical triangle/face row, not a source
   vertex id, GPU draw vertex id, instance id, or backend-private primitive id.
4. For unindexed triangle-list meshes, the reported id is the emitted triangle ordinal.
5. The behavior is covered by a native test with at least two triangles in one mesh, where the
   frontmost selected triangle is not triangle zero.
6. The query result includes or is compatible with existing `freshness_serial` stale-result
   suppression, while GSP remains responsible for its public `pick_scene_snapshot_id`.

Optional but useful upstream evidence:

- an explicit mesh triangle query example in the Python facade;
- documented interaction between `dvz_visual_set_item_range()`, index buffers, instancing, and
  reported face/triangle ids;
- proof that the query pass respects retained View3D camera/projection/layout state for DATA-space
  attached meshes.

## Safe Follow-Up

Do not promote Datoviz `query.view3d.mesh_triangle_pick.v1` in GSP yet.

The next safe mission is an upstream Datoviz handoff packet, not a GSP implementation mission. A
focused GSP implementation mission becomes safe only after Datoviz exposes and tests public
mesh-face/triangle query identity.

Suggested next mission:

```text
M205 - S050 Datoviz mesh triangle query upstream handoff

Goal:
Create a Datoviz-side handoff issue/patch plan for native mesh face/triangle query identity.

Scope:
- Do not edit the Datoviz checkout unless explicitly approved.
- Convert S050 evidence into a concise upstream API request.
- Specify expected C/Python symbols and native tests.
- Keep GSP Datoviz capability unadvertised.

Acceptance:
- Handoff names exact Datoviz files/functions requiring change.
- Handoff specifies required query result fields and id semantics.
- Handoff includes minimal native fixture requirements.
- GSP worktree remains unchanged except for the handoff note/mission file.
```

## Verification

Commands run:

```bash
tools/agentctl brief
tools/agentctl mission show M200
git status --short --branch
git -C /home/cyrille/GIT/Viz/datoviz status --short --branch
git -C /home/cyrille/GIT/Viz/datoviz rev-parse --abbrev-ref HEAD
git -C /home/cyrille/GIT/Viz/datoviz rev-parse HEAD
PYTHONPATH=/home/cyrille/GIT/Viz/datoviz python - <<'PY'
import datoviz as dvz
print(getattr(dvz, "__file__", None))
for name in [
    "DvzQueryResult",
    "DvzQueryRequest",
    "dvz_query_request",
    "dvz_panel_query",
    "dvz_panel_query_now",
    "dvz_scene_poll_query",
    "dvz_visual_id",
    "dvz_visual_set_query_capabilities",
]:
    print(name, hasattr(dvz, name))
print([name for name, *_ in dvz.DvzQueryResult._fields_])
PY
```
