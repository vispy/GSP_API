# M066 - PointVisual v1 and Datoviz v0.4 retained point path

## Stage

S023 - Visual Families v1 and Manual Visual QA Foundation

## Status

Completed.

## Summary

Freeze PointVisual v1 semantics and prove the simplest Datoviz v0.4 retained-scene visual path.

## Planned Deliverables

- Point visual spec and size-unit decision.
- Matplotlib reference mapping with protocol `sizes` as screen-pixel diameters.
- Datoviz v0.4 adapter for `dvz_point` plus `"position"`, `"color"`, and `"diameter"`.
- Explicit Datoviz attach descriptor handling.
- QA cases integrated into M065 harness.

## Acceptance

Point cases render in Matplotlib. Datoviz Point NDC renders or reports a precise facade/capture
blocker. No v0.3 symbols appear in adapter code.

## Result

Completed in the local main Codex session on 2026-06-23.

- `PointVisual.sizes` is frozen as rendered screen-pixel diameter.
- ADR-0010 records the size-unit and first Datoviz attach decision.
- Matplotlib converts protocol diameters to `scatter(s=...)` area units using figure DPI.
- Datoviz v0.4 uploads `position`, `color`, and direct `diameter` arrays to `dvz_point`.
- Datoviz v0.4 attaches point/image visuals with an explicit `DvzVisualAttachDesc`.
- S023 visual QA includes `point/alpha_overlap_ndc` alongside the basic and diameter-ramp cases.
- Validation passed: Ruff, full pytest, strict mypy, backend imports, focused renderer tests, and
  point visual QA rendering for both Matplotlib and Datoviz.

## Stop Condition

Stop if `sizes` semantics are not accepted as diameter pixels. Stop if coordinate-space mapping is
ambiguous without a documented fixture/result.
