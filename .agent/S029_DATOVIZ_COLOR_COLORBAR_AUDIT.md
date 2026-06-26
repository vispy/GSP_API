# S029 Datoviz Color And Colorbar Promotion Audit

Updated: 2026-06-26

## Scope

Mission M114 audited the Datoviz color rows rendered in the S029 review pack:

- `color/scalar_image_viridis_colorbar`
- `color/point_scalar_gray_range`
- `color/marker_scalar_fill_alpha`

The review pack was regenerated at `artifacts/visual_qa/s029/current-review-pack` with the local
Datoviz `v0.4-dev` checkout after the explicit colorbar tick fix.

## Promotion Decision

The three color rows are promoted to `strict` for rendering only, with reason code
`datoviz_rendered_strict_s029_family_audit`.

| Row | Strict rendering scope | Notes |
|---|---|---|
| `color/scalar_image_viridis_colorbar` | scalar image, viridis color scale, native Datoviz colorbar, explicit tick values and labels | GSP CPU maps scalar values through the canonical `ColorScale` before Datoviz RGBA8 upload. |
| `color/point_scalar_gray_range` | scalar point colors, gray color scale, under/over endpoint clipping | GSP CPU maps scalar point values to canonical RGBA8 before Datoviz upload. |
| `color/marker_scalar_fill_alpha` | scalar marker fill colors, magma color scale, alpha, constant stroke | GSP CPU maps scalar marker fill values to canonical RGBA8 before Datoviz upload. |

All promoted rows keep `query_supported: false`; this audit does not promote scalar query payload
parity or native Datoviz scalar readback.

## Rows Still Adapted Or Unsupported

Rendered text, mesh, and transform rows remain `adapted` pending focused audits. Guide rows remain
`unsupported` because axis guide, title, grid, explicit tick label, and guide query semantics are
still unverified.

## Evidence

- `src/gsp_datoviz/protocol_renderer.py` calls `dvz_colorbar_set_ticks()` when
  `ColorbarGuide.ticks` are present.
- `tests/test_datoviz_v04_protocol_renderer.py` covers explicit colorbar tick values and labels.
- `tests/test_visual_qa_harness.py` covers strict promotion for the three color rows and preserves
  adapted status for unrelated rendered rows.
- `artifacts/visual_qa/s029/current-review-pack/capability_matrix.json` records strict rendered
  color rows and explicit rendering-only query status.

