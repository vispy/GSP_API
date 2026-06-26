# S029 Datoviz Mesh Promotion Audit

Updated: 2026-06-26

## Scope

Mission M116 audited the Datoviz mesh rows rendered in the S029 review pack:

- `mesh/single_triangle_uniform_ndc_2d`
- `mesh/indexed_square_uniform_ndc_2d`
- `mesh/indexed_square_per_face_ndc_2d`

The audit is rendering-only and bounded to accepted S025 2D NDC flat triangle meshes.

## Promotion Decision

All three rows are promoted to `strict` for rendering only, with reason code
`datoviz_rendered_strict_s029_family_audit`. Query/readback remains unpromoted for every mesh row.

| Row | Decision | Strict rendering scope |
|---|---|---|
| `mesh/single_triangle_uniform_ndc_2d` | `strict` | One indexed 2D NDC triangle, flat uniform RGBA, `z=0` Datoviz upload, depth testing disabled. |
| `mesh/indexed_square_uniform_ndc_2d` | `strict` | Shared-vertex indexed two-triangle 2D NDC square, flat uniform opaque RGBA. |
| `mesh/indexed_square_per_face_ndc_2d` | `strict` | Two-face 2D NDC square with per-face RGBA, adapted to Datoviz per-vertex colors by duplicating triangle vertices. |

## Evidence

- `src/gsp_datoviz/protocol_renderer.py` uploads 2D positions as 3D `z=0`, preserves uniform indexed
  faces for uniform color, disables depth testing, and attaches via the ordered 2D data path.
- `src/gsp_datoviz/protocol_renderer.py` adapts per-face RGBA by duplicating triangle vertices and
  assigning each duplicated vertex the source face color; this preserves the rendered S025 face-color
  contract but is not promoted for query/readback topology.
- `tests/test_datoviz_v04_protocol_renderer.py` covers uniform indexed upload and per-face color
  vertex-duplication payloads.
- Current contact sheets show Datoviz matching Matplotlib for the three bounded 2D mesh cases.
- `tests/test_visual_qa_harness.py` asserts strict metadata for the three promoted mesh rows and keeps
  `query_supported: false`.

## Deferred

3D mesh projection/camera semantics, normals, Lambert shading, public materials/lights, textures,
wireframe, explicit depth/culling policy expansion, scalar face colors, mesh query/readback,
barycentric payloads, and topology-preserving per-face query semantics remain future work.
