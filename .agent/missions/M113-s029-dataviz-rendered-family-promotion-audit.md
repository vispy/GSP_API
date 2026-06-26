# M113 - S029 Datoviz rendered-family promotion audit

## Stage

S029 - Backend Capability Matrix and Visual Review Pack

## Status

Completed.

## Summary

Audit Datoviz rows that currently render in the S029 review pack and decide which exact scopes can
move from `adapted` to strict or remain adapted with documented semantic deltas.

## Scope

Families currently rendered by Datoviz in `artifacts/visual_qa/s029/current-review-pack`:

- point;
- marker;
- segment;
- path;
- image;
- overlay.

## Deliverables

- Per-family promotion notes tied to capability matrix rows.
- Updated Datoviz capability declarations only for exact proven scopes.
- Tests covering any promoted strict/adapted metadata.
- Updated S029 review pack after the audit.

## Acceptance

- No Datoviz capability is broader than the tested S023-S028 case scope.
- Image support distinguishes interpolation, origin, extent, scalar gray, RGB/RGBA, and sampled-field
  adaptation.
- Marker/segment/path support records any visual or query limitations.
- Unsupported query payloads remain explicit.

## Stop Condition

Stop if a rendered Datoviz family would require silent approximation, ignored fields, or unverified
query semantics to be marked strict.

## Completion

Completed on 2026-06-26 in the local Mission Control session.

- Added `.agent/S029_DATOVIZ_RENDERED_FAMILY_AUDIT.md`.
- Promoted only exact rendered point, marker, segment, path, image, and overlay S029 rows to
  `strict`.
- Kept rendered text, mesh, color/colorbar, and transform rows `adapted` pending focused audits.
- Kept guide rows `unsupported`.
- Regenerated `artifacts/visual_qa/s029/current-review-pack`.
