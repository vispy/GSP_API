# M115 - S029 Datoviz text promotion audit

## Stage

S029 - Backend Capability Matrix and Visual Review Pack

## Status

Completed.

## Summary

Audit Datoviz text rows that currently render in the S029 review pack and decide which exact
rendering scopes can move from `adapted` to `strict`.

## Scope

Rendered Datoviz rows:

- `text/basic_ndc`
- `text/anchor_grid_ndc`
- `text/rotation_alpha_ndc`
- `text/data_vs_ndc`
- `text/multiline_unicode_smoke`

## Deliverables

- Per-row text promotion notes tied to capability matrix rows.
- Updated capability matrix policy only for exact proven text rendering scopes.
- Tests covering promoted strict/adapted metadata.
- Regenerated S029 review pack.

## Acceptance

- Font size, anchor, rotation, alpha, z-order, multiline, Unicode, and DATA vs NDC behavior are
  either promoted with evidence or left adapted with explicit blockers.
- Query/readback remains unpromoted unless separately proven.

## Stop Condition

Stop if strict promotion would require silently ignoring text anchors, font metrics, Unicode,
rotation, DATA mapping, or query semantics.

## Completion

Completed on 2026-06-26 in the local Mission Control session.

- Added `.agent/S029_DATOVIZ_TEXT_AUDIT.md`.
- Promoted only `text/rotation_alpha_ndc` to `strict` for rendering only.
- Left `text/basic_ndc`, `text/anchor_grid_ndc`, `text/data_vs_ndc`, and
  `text/multiline_unicode_smoke` as `adapted` with row-specific blockers.
- Preserved `query_supported: false` for all text rows.
- Regenerated S029 capability matrix/index artifacts from the current review-pack report.
- Full Datoviz runtime regeneration was blocked locally by missing macOS MoltenVK ICD files in the
  Datoviz checkout.
