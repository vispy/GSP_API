# S029 Datoviz Text Promotion Audit

Updated: 2026-06-26

## Scope

Mission M115 audited the Datoviz text rows rendered in the S029 review pack:

- `text/basic_ndc`
- `text/anchor_grid_ndc`
- `text/rotation_alpha_ndc`
- `text/data_vs_ndc`
- `text/multiline_unicode_smoke`

The review pack contact sheets at `artifacts/visual_qa/s029/current-review-pack` were compared
against the S024 TextVisual contract and the current Datoviz retained-text adapter mapping.

## Promotion Decision

Only `text/rotation_alpha_ndc` is promoted to `strict` for rendering, with reason code
`datoviz_rendered_strict_s029_family_audit`. Query/readback remains unpromoted for every text row.

| Row | Decision | Strict rendering scope / blocker |
|---|---|---|
| `text/basic_ndc` | `adapted` | Default `BASELINE` anchor semantics are not strictly verified; Datoviz maps `BASELINE` to the same numeric text anchor as `CENTER`. |
| `text/anchor_grid_ndc` | `adapted` | Horizontal anchors render plausibly, but `BASELINE` vs `CENTER` and top/bottom text-box semantics are not proven by the current fixture. |
| `text/rotation_alpha_ndc` | `strict` | NDC ASCII text with center anchors, per-item rotation radians, RGBA alpha, logical font size, and layering above an image. |
| `text/data_vs_ndc` | `adapted` | DATA and NDC positions currently agree under the QA runner's `[-1,+1]` view; this does not prove strict DATA/View2D mapping for text. |
| `text/multiline_unicode_smoke` | `adapted` | Newline and simple non-ASCII glyphs render, but Unicode fallback and `BASELINE` multiline anchoring remain unverified. |

## Evidence

- `src/gsp_datoviz/protocol_renderer.py` sends retained text style, UTF-8 strings, placement,
  center text anchors, rotation radians, alpha color, and `z_order` depth for the promoted row.
- `artifacts/visual_qa/s029/current-review-pack/contact_sheets/text_rotation_alpha_ndc.png`
  shows the Datoviz row matching the Matplotlib reference for rotation, alpha, and draw-above-image
  behavior within the tested S029 scope.
- `tests/test_visual_qa_harness.py` asserts the promoted row is strict, keeps
  `query_supported: false`, and leaves baseline/DATA/multiline rows adapted.

## Deferred

Strict text query/readback, baseline anchoring, full anchor-grid proof fixtures, DATA/View2D text
mapping beyond the identity view, Unicode fallback diagnostics, and exact multiline anchoring remain
future work.
