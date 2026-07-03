# S050 Datoviz Mesh Triangle Query Handoff

Date: 2026-07-03

Source evidence: `.agent/S050_DATOVIZ_MESH_PICK_EVIDENCE.md`

## Request

Add public Datoviz v0.4 support for native mesh face/triangle query identity so GSP can safely
consider Datoviz support for `query.view3d.mesh_triangle_pick.v1`.

This is an upstream Datoviz API/runtime request, not a GSP capability promotion. Until this exists,
GSP should keep returning structured unsupported for Datoviz View3D mesh triangle picking.

## Required Semantics

For a mesh visual queried with `DVZ_SCENE_TARGET_FACE` or `DVZ_SCENE_TARGET_TRIANGLE`:

1. The query must return the public visual identity already exposed by `dvz_visual_id()` and
   `DvzQueryResult.visual_id`.
2. The result must identify the selected canonical mesh triangle/face row.
3. For indexed triangle meshes, the reported id must be the face row, not a source vertex id, GPU
   draw vertex id, instance id, or backend-private primitive id.
4. For unindexed triangle-list meshes, the reported id must be the emitted triangle ordinal.
5. Misses must remain explicit misses, and stale/superseded results must remain compatible with the
   existing `freshness_serial` behavior.
6. The query pass must respect the retained View3D camera/projection/layout/depth state used for the
   visible DATA-space mesh.

Acceptable result encodings include either:

- `resolved_target = DVZ_SCENE_TARGET_TRIANGLE` with `resolved_id = <zero-based triangle row>`;
- `face_id = <zero-based face row>`;
- `primitive_id = <zero-based triangle row>`.

The chosen encoding should be documented and covered by native tests.

## Datoviz Files And Functions To Inspect

- `include/datoviz/scene/types.h`
  - `DvzQueryRequest`
  - `DvzQueryResult`
- `include/datoviz/scene/enums.h`
  - `DVZ_SCENE_TARGET_FACE`
  - `DVZ_SCENE_TARGET_TRIANGLE`
  - `DVZ_QUERY_CAPABILITY_FACE`
- `include/datoviz/scene.h`
  - `dvz_visual_id()`
  - `dvz_visual_set_query_capabilities()`
- `src/scene/query/policy.c`
  - target-to-capability mapping
  - `_dvz_scene_query_item_target_eligible()`
- `src/scene/query/result.c`
  - `_dvz_scene_query_decode_item_id()`
  - any new decoder needed for face/triangle ids
- `src/scene/visuals/mesh/query.c`
  - `_mesh_query_eligible()`
  - `_mesh_query_build()`
  - `_mesh_query_decode()`
  - `_mesh_query_readout()`
- `src/scene/visuals/query_geometry.c`
  - `_scene_query_indexed_primitive_geometry()`
  - `_scene_query_mesh_item_geometry()`
- `src/scene/shaders/glsl/primitive_query_u32.vert`
- `src/scene/shaders/glsl/primitive_query_u32.frag`
- `src/scene/shaders/wgsl/primitive_query_u32.vert.wgsl`
- `src/scene/shaders/wgsl/primitive_query_u32.frag.wgsl`
- `src/scene/tests/query.c`
- Python facade generation/binding files, if public ctypes exposure changes.

## Current Blocker

The current local Datoviz v0.4 mesh query path builds a `DVZ_FORMAT_R32_UINT` query target and can
decode an item id, but it does not expose the selected triangle:

- mesh eligibility rejects targets other than `NONE`, `ITEM`, or `OBJECT`;
- `_scene_query_mesh_item_geometry()` overwrites non-instanced per-primitive ids with `1u`;
- decoded non-instanced mesh hits therefore return `item_id = 0` for every triangle;
- instanced mesh ids represent instance ordinals, not triangle ordinals.

That is insufficient for GSP because S044 requires `primitive_index` to be the canonical
`MeshVisual.faces` row.

## Minimal Native Test

Add a native Datoviz test with one mesh containing at least two triangles where the frontmost hit is
not triangle zero.

The test should verify:

- request target is `DVZ_SCENE_TARGET_FACE` or `DVZ_SCENE_TARGET_TRIANGLE`;
- query succeeds for the mesh visual;
- `visual_id` matches `dvz_visual_id(visual)`;
- returned face/triangle identity is the expected zero-based triangle row;
- a miss stays a miss;
- a second superseding request does not return an older stale result as current.

Useful variants:

- indexed two-triangle mesh;
- unindexed triangle-list mesh;
- two overlapping triangles with depth deciding the winner;
- retained View3D camera/projection/layout path matching the visible DATA-space mesh.

## GSP Follow-Up After Datoviz Lands This

Only after native Datoviz exposes and tests public mesh face/triangle identity should GSP open a
new implementation mission to:

- store the native Datoviz visual id beside each retained GSP `MeshVisual.id`;
- map native `visual_id` back to public GSP `visual_id`;
- convert native face/triangle result fields into S044 `primitive_index`;
- compute and validate GSP `pick_scene_snapshot_id`;
- add focused Datoviz capability tests before advertising `query.view3d.mesh_triangle_pick.v1`.
