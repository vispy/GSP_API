# S050 Datoviz Mesh Pick Evidence

Generated: 2026-07-03

## Verdict

Datoviz upstream API work is required before GSP can safely implement or advertise
`query.view3d.mesh_triangle_pick.v1`.

The current local Datoviz v0.4 source/runtime exposes a general panel query pipeline and a public
Datoviz visual id, but it does not expose a public mesh triangle/face query result that maps to the
GSP canonical `MeshVisual` triangle stream index. The current mesh query path resolves mesh item or
instance identity, not public triangle identity.

No GSP public capability was promoted.

## GSP Adapter Audit

Relevant GSP files:

- `src/gsp_datoviz/capabilities.py`
- `src/gsp_datoviz/protocol_renderer.py`
- `src/gsp_datoviz/query.py`

Observed behavior:

- Datoviz capability translation may advertise `view3d-ray`, but explicitly does not add
  `query.view3d.mesh_triangle_pick.v1`.
- `metadata["s044_mesh_triangle_pick"]` says mesh picking is not advertised until Datoviz can prove
  public `visual_id`, canonical `primitive_index`, and layout/view/projection/pick-scene freshness.
- `metadata["s044_mesh_triangle_pick_diagnostics"]` records
  `pick.unsupported.no_public_primitive_map` and `pick.unsupported.native_state_only`.
- `DatovizV04ProtocolRenderer.query_view3d_mesh_triangle_pick()` always returns structured
  unsupported with `UNSUPPORTED_NO_PUBLIC_PRIMITIVE_MAP`.
- The Datoviz query decoder currently maps native `DvzQueryResult.visual_id` to
  `datoviz:visual:<id>` and only recognizes point/image families for ordinary data queries. It does
  not map Datoviz mesh query fields to GSP public mesh triangle payloads.

This matches the accepted S044 boundary: Datoviz must not encode unsupported or stale mesh-pick
states as misses.

## Datoviz Checkout

Inspected sibling checkout read-only:

```text
/Users/cyrille/GIT/Viz/datoviz
branch: v0.4-dev
commit: dc8b168ed86e0f674be204d00c29e5869ee5e6c4
```

Pre-existing sibling checkout state during inspection:

```text
## v0.4-dev...origin/v0.4-dev
 m data
?? paper/paper.pdf
```

No sibling Datoviz files were edited.

## Positive Evidence

Public source/header/facade symbols that exist:

| Need | Evidence |
|---|---|
| Queue panel query | `dvz_panel_query()` in `include/datoviz/scene/interaction.h` and `src/scene/query/queue.c` |
| Poll query result | `dvz_scene_poll_query()` in `include/datoviz/scene/interaction.h` and `src/scene/query/result.c` |
| Query request/result ABI | `DvzQueryRequest`, `DvzQueryResult` in `include/datoviz/scene/types.h` |
| Visual identity | `dvz_visual_id()` in `include/datoviz/scene.h`; `_scene_visual_public_id()` populates `DvzQueryResult.visual_id` |
| Query target vocabulary | `DVZ_SCENE_TARGET_FACE`, `DVZ_SCENE_TARGET_TRIANGLE`, and `DVZ_QUERY_CAPABILITY_FACE` in `include/datoviz/scene/enums.h` |
| Mesh query family | `_dvz_scene_query_mesh_ops()` in `src/scene/visuals/mesh/query.c` |
| Panel/layout frame snapshot | `dvz_panel_resolve_frame()`, `dvz_panel_frame_info()`, `DvzPanelFrameInfo` |
| View3D state revision | `dvz_panel_view3d_state()`, `DvzPanelView3DState.revision` |
| Python ctypes exposure | `datoviz/_ctypes.py` exposes `DvzQueryResult._fields_`, query functions, panel-frame structs, and View3D state structs |

Plain `python` imported the sibling source package and confirmed these Python-visible symbols:

```text
dvz_panel_query: true
dvz_scene_poll_query: true
dvz_query_request: true
DvzQueryResult: true
dvz_visual_id: true
dvz_visual_set_query_capabilities: true
DVZ_SCENE_TARGET_TRIANGLE: true
DVZ_SCENE_TARGET_FACE: true
DVZ_QUERY_CAPABILITY_FACE: true
dvz_panel_resolve_frame: true
dvz_panel_frame_info: true
DvzPanelFrameInfo: true
dvz_panel_view3d_state: true
DvzPanelView3DState: true
```

The Python-visible `DvzQueryResult._fields_` includes:

```text
visual_id, visual_family, raw_target, raw_id, resolved_target, resolved_id,
item_id, face_id, primitive_id, vertex_id, has_depth, depth
```

This is useful ABI surface, but field existence alone is not enough for GSP strict support.

## Blocking Evidence

### 1. Mesh query does not populate triangle identity

`src/scene/visuals/mesh/query.c` builds mesh query plans with
`_scene_query_mesh_item_geometry()` and decodes through `_dvz_scene_query_decode_item_id()`.

`src/scene/visuals/query_geometry.c` first computes per-primitive ids for indexed primitive
geometry, but `_scene_query_mesh_item_geometry()` then overwrites non-instanced mesh query ids:

```text
if no instance_transform:
    scratch->query_ids[i] = 1u
```

For instanced meshes it writes instance ids:

```text
ids[dst] = (uint32_t)inst + 1u
```

Therefore current mesh query hits identify a mesh item/object or instance, not a canonical triangle
row.

### 2. Face/triangle query targets are declared but not implemented for mesh

`DVZ_SCENE_TARGET_FACE` and `DVZ_SCENE_TARGET_TRIANGLE` map to `DVZ_QUERY_CAPABILITY_FACE` in
`src/scene/query/policy.c`, but the standard mesh eligibility path rejects any target other than
`NONE`, `ITEM`, or `OBJECT` through `_dvz_scene_query_item_target_eligible()`.

Repository search found no mesh implementation that accepts `DVZ_SCENE_TARGET_FACE` or
`DVZ_SCENE_TARGET_TRIANGLE`, no tests for those targets, and no code populating
`DvzQueryResult.face_id` or `DvzQueryResult.primitive_id` for mesh hits.

### 3. Existing mesh query tests prove item identity only

`src/scene/tests/query.c` includes:

- `test_scene_mesh_query_resolves_item`
- `test_scene_mesh_query_resolves_instance_item`

Both use `DVZ_SCENE_TARGET_ITEM` and assert `resolved_target == DVZ_SCENE_TARGET_ITEM` plus
`item_id`. They do not assert `face_id`, `primitive_id`, or `DVZ_SCENE_TARGET_TRIANGLE`.

### 4. Freshness information is split and insufficient for GSP strict response

Datoviz exposes useful freshness ingredients:

- `DvzQueryResult.freshness_serial`
- `DvzPanelFrameInfo.snapshot_id`
- `DvzPanelFrameInfo.panel_revision`
- `DvzPanelFrameInfo.layout_revision`
- `DvzPanelFrameInfo.view_revision`
- `DvzPanelFrameInfo.visual_revision`
- `DvzPanelView3DState.revision`

However, `DvzQueryResult` does not itself report the `DvzPanelFrameInfo.snapshot_id` or a
query/pick-scene snapshot id tying the result to the exact layout, View3D state, projection state,
visual revision, and depth-affecting scene used by the pick.

GSP could maintain some freshness guards on its side, but strict advertisement still requires the
native result to be tied to the rendered pick scene that produced the hit/miss. Current public
Datoviz API does not expose that binding.

## GSP-Only Viability

GSP-only implementation is not viable for strict Datoviz native
`query.view3d.mesh_triangle_pick.v1` advertisement.

Reasons:

- GSP can map a `DvzVisual*` to a public GSP visual id only for visuals it created and retained, but
  current native mesh query results do not expose the canonical triangle index.
- Treating Datoviz mesh `item_id` as `primitive_index` would be wrong for current non-instanced mesh
  queries because the source overwrites all query ids to `1`.
- GSP can compute its own CPU oracle, but that would be a Matplotlib-style adapted/reference route,
  not Datoviz native evidence.
- Promoting strict Datoviz support without native triangle/freshness evidence would violate
  `spec/view3d_mesh_triangle_picking.md` and ADR-0028.

## Upstream Handoff Needed

Datoviz should expose and test a public mesh triangle query contract before GSP promotes the
capability.

Minimum upstream evidence needed:

1. A public request path for mesh triangle or face queries:
   `DvzQueryRequest.target = DVZ_SCENE_TARGET_TRIANGLE` or `DVZ_SCENE_TARGET_FACE`.
2. Mesh eligibility and capability gates that accept that target through `DVZ_QUERY_CAPABILITY_FACE`
   for `DVZ_VISUAL_TYPE_MESH`.
3. Query geometry that preserves canonical triangle ids for both indexed triangle lists and
   unindexed triangle lists, without overwriting them with mesh item/instance ids.
4. `DvzQueryResult` hit fields populated with:
   - public `visual_id`;
   - `resolved_target = DVZ_SCENE_TARGET_TRIANGLE` or `DVZ_SCENE_TARGET_FACE`;
   - `primitive_id` or `face_id` equal to the public triangle row/ordinal;
   - optional `instance_id` only when instanced picking is intentionally supported.
5. Tests covering at least:
   - indexed two-triangle mesh returning triangle `0` and `1` at distinct points;
   - unindexed triangle-list mesh returning emitted triangle ordinals;
   - overlapping opaque triangles selecting the frontmost hit by depth;
   - miss versus unsupported target;
   - no fallback to mesh item id for triangle requests.
6. Freshness/readback evidence tying each result to a public frame or pick-scene snapshot:
   - panel frame snapshot id or equivalent;
   - View3D revision;
   - projection/camera revision or matrix snapshot id;
   - visual/depth-affecting scene revision;
   - stale/superseded result behavior.
7. Python ctypes/facade exposure for the new fields/functions, with smoke tests showing
   `DvzQueryResult._fields_` and constants are available from Python.

## Recommended Follow-Up

Keep current GSP Datoviz behavior unchanged:

- do not advertise `query.view3d.mesh_triangle_pick.v1`;
- keep `query_view3d_mesh_triangle_pick()` returning structured unsupported;
- keep S044 diagnostics in capability metadata.

After Datoviz lands the upstream face/triangle query contract, open a bounded GSP mission to:

- add a Datoviz mesh-triangle query decoder for `DVZ_SCENE_TARGET_TRIANGLE` or
  `DVZ_SCENE_TARGET_FACE`;
- map Datoviz visual ids to GSP-created public `MeshVisual.id` values;
- map `primitive_id`/`face_id` to GSP canonical `primitive_index`;
- add stale checks against GSP layout/view/projection/pick-scene snapshots;
- run synthetic fake-facade tests first, then one optional live runtime smoke if credentials and GPU
  runtime are already configured.

## Validation

- Read required GSP specs and decisions for S044/S050.
- Audited GSP Datoviz capability, query, and renderer code.
- Inspected Datoviz v0.4 headers, query source, mesh query source, query geometry helpers, tests,
  and generated Python ctypes facade.
- Ran focused GSP guardrail tests:
  `PYTHONPATH=src python -m pytest tests/test_datoviz_v04_protocol_renderer.py::test_datoviz_capabilities_promote_panel_query_only_when_query_binding_is_ready tests/test_datoviz_v04_protocol_renderer.py::test_datoviz_renderer_mesh_triangle_pick_reports_structured_unsupported`
  passed with 2 tests.
- Did not run GPU/runtime Datoviz tests because the evidence gap is visible in public source/API
  shape and the mission is an evidence spike, not an upstream implementation.
- `uv run python` was attempted for runtime symbol inspection but was blocked by sandbox permission
  on `/Users/cyrille/.cache/uv/sdists-v9/.git`; plain `python` successfully inspected the local
  Datoviz Python package symbols.
