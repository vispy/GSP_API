# S029 Datoviz Transform Promotion Audit

Updated: 2026-06-26

## Scope

Mission M117 audited the Datoviz transform rows rendered in the S029 review pack:

- `transform/inline_named_equivalence`
- `transform/view2d_data_ndc_overlay`
- `transform/family_affine_view2d`

The audit is rendering-only and bounded to accepted S027 finite eager 2D affine transforms and
linear `View2D` DATA-to-panel-NDC mapping.

## Promotion Decision

All three rows are promoted to `strict` for rendering only, with reason code
`datoviz_rendered_strict_s029_family_audit`. Query inverse payloads remain unpromoted for every
transform row.

| Row | Decision | Strict rendering scope |
|---|---|---|
| `transform/inline_named_equivalence` | `strict` | Finite eager point positions in NDC, inline AFFINE_2D binding, required named AFFINE_2D resource resolution, and identical CPU-adapted upload coordinates. |
| `transform/view2d_data_ndc_overlay` | `strict` | Finite eager point DATA positions mapped through linear `View2D`, including reversed x limits, aligned with explicit NDC overlay points. |
| `transform/family_affine_view2d` | `strict` | One required named AFFINE_2D resource applied before linear `View2D` mapping for point, marker, segment, path, center-anchored text, and strict 2D uniform mesh visuals. |

## Evidence

- `src/gsp_datoviz/protocol_renderer.py` resolves inline and named affine bindings, applies the
  3x3 matrix to finite eager positions on the CPU, and rejects unresolved required named resources
  instead of silently dropping them.
- `src/gsp_datoviz/protocol_renderer.py` maps DATA positions through `View2D` with the same linear
  formula for normal and reversed limits before upload to the Datoviz panel path.
- `tests/test_datoviz_v04_protocol_renderer.py` covers inline affine adaptation, named transform
  resolution, missing required resource rejection, and reversed-limit `View2D` DATA mapping.
- Current contact sheets show Datoviz matching Matplotlib for inline/named point equivalence,
  reversed `View2D` DATA-to-NDC overlay alignment, and cross-family affine plus `View2D` rendering.
- `tests/test_visual_qa_harness.py` asserts strict metadata for the three promoted transform rows
  while keeping `query_supported: false`.

## Deferred

Transform query inverse payloads, image affine transforms, 3D camera/projection/controller semantics,
nonlinear/log/category/geospatial transforms, virtual-source materialization, equal-aspect layout
semantics, and family scopes outside the S029 rendered transform rows remain future work.
