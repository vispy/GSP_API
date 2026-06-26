# M114 - S029 Datoviz color and colorbar promotion audit

## Stage

S029 - Backend Capability Matrix and Visual Review Pack

## Status

Completed.

## Summary

Audit Datoviz color rows that currently render in the S029 review pack and decide which exact
rendering scopes can move from `adapted` to `strict`.

## Scope

Rows currently rendered by Datoviz in `artifacts/visual_qa/s029/current-review-pack`:

- `color/scalar_image_viridis_colorbar`
- `color/point_scalar_gray_range`
- `color/marker_scalar_fill_alpha`

## Deliverables

- Per-row promotion notes tied to capability matrix rows.
- Updated capability matrix policy only for exact proven rendering scopes.
- Tests covering promoted strict/adapted metadata.
- Updated S029 review pack after the audit.

## Acceptance

- No color/colorbar capability is broader than the tested S026-S029 case scope.
- Explicit colorbar tick values and labels are wired to Datoviz.
- Scalar point and marker color mappings remain documented as GSP CPU canonical RGBA8 mappings.
- Query payloads remain explicit and are not promoted without runtime query evidence.

## Stop Condition

Stop if strict promotion would require silent approximation, ignored colorbar fields, or unverified
query semantics.

## Completion

Completed on 2026-06-26 in the local Mission Control session.

- Added `.agent/S029_DATOVIZ_COLOR_COLORBAR_AUDIT.md`.
- Promoted `color/scalar_image_viridis_colorbar`, `color/point_scalar_gray_range`, and
  `color/marker_scalar_fill_alpha` to `strict` for rendering only.
- Preserved `query_supported: false` for all promoted rows.
- Regenerated `artifacts/visual_qa/s029/current-review-pack`.
