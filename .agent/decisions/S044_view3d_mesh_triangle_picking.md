# S044 View3D Mesh Triangle Picking Decisions

Status: accepted by M191 from P028 response.

## Accepted

- The public capability is `query.view3d.mesh_triangle_pick.v1`.
- The protocol is backend-neutral; "GPU picking" is an implementation route, not a public name.
- Strict v1 is limited to orthographic `View3D`, `depth_mode="opaque_less"`, and opaque
  DATA-space `MeshVisual` triangle geometry.
- A strict hit must report the public `visual_id` and the public canonical triangle
  `primitive_index`.
- `query.view3d.ray_readback.v1` remains a separate camera/layout ray-context query.
- Picking responses must carry layout, view revision, view/projection, and pick-scene snapshot
  freshness evidence for hit/miss results.

## Deferred

- Visual-only picking.
- NDC3 mesh picking.
- Transparent mesh picking.
- Non-mesh visual picking.
- Perspective, culling, instancing, multi-hit selection, barycentric coordinates, hit positions,
  depth values, ray distance, and backend-native ids.

## Implementation Direction

M192 should implement the accepted bounded proof:

1. Add protocol request/response payloads and validation for
   `query.view3d.mesh_triangle_pick.v1`.
2. Define `pick_scene_snapshot_id` from public depth-affecting state.
3. Add Matplotlib CPU oracle coverage for strict-scope fixtures or explicit adapted diagnostics.
4. Add Datoviz capability gates and implementation only when public visual/triangle mapping and
   synchronized pick-state freshness are proven.
5. Add positive, stale, invalid, miss, ambiguous, and unsupported fixtures before advertising strict
   support.

## Source

`.agent/consultations/P028-response.md` converted into ADR-0028 and
`spec/view3d_mesh_triangle_picking.md`.
