# M065 - Visual QA harness foundation

## Stage

S023 - Visual Families v1 and Manual Visual QA Foundation

## Status

Draft.

## Summary

Build repeatable artifact production and manual review workflow around existing Point/Image smoke
cases, using M064 Datoviz probe results.

## Planned Deliverables

- Visual QA CLI or script entry point.
- Case registry and report schema.
- Artifact writer for scene JSON, `.npz` sidecars, backend outputs, logs, unsupported reports,
  contact sheets, and manual notes templates.
- Matplotlib backend runner for existing Point/Image protocol scenes.
- Datoviz backend runner that renders or emits structured unsupported diagnostics.
- Initial cases:
  - `point/basic_ndc`
  - `point/diameter_ramp_ndc`
  - `image/checker_nearest_ndc`
  - `overlay/point_over_image_ndc`

## Acceptance

Running the S023 suite produces `report.json`, scene fixtures, `.npz` arrays, Matplotlib PNGs,
Datoviz PNGs or unsupported JSON, contact sheets, and manual notes. Schema validation passes.

## Stop Condition

Stop if Matplotlib artifacts are missing or the report schema is unstable. Datoviz unsupported is
acceptable only with structured diagnostics from M064 capability data.
