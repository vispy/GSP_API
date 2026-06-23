# M066 - PointVisual v1 and Datoviz v0.4 retained point path

## Stage

S023 - Visual Families v1 and Manual Visual QA Foundation

## Status

Draft.

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

## Stop Condition

Stop if `sizes` semantics are not accepted as diameter pixels. Stop if coordinate-space mapping is
ambiguous without a documented fixture/result.
