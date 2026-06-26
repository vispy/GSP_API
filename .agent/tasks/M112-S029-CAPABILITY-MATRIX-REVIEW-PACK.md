# M112-S029 - Capability matrix and review-pack foundation

## Mission

M112

## Goal

Implement the first S029 layer: a complete review pack over S023-S028 visual QA output with explicit
backend capability status taxonomy.

## Status

Completed.

## Deliverables

- `capability_matrix.json` and `capability_matrix.md` writers.
- Review-pack command and Datoviz runtime wrapper.
- Focused tests for strict/not-run/disabled classification.
- Mission Control records for S029 opening.

## Acceptance

- The review pack distinguishes `strict`, `adapted`, `experimental`, `unsupported`, `disabled`,
  `crashed`, and `not_run`.
- Datoviz rendered output is reviewable but not silently promoted to strict.
- Unsupported/disabled rows include reason codes and blockers.

## Closeout

- Implemented the review-pack generation path.
- Added documentation and wrappers for local Datoviz review generation. S029 follow-up corrected
  those wrappers and the QA default to `legacy_srgb_blend`, because Matplotlib/Agg alpha parity
  requires reproducing display-space sRGB blending rather than Datoviz's mathematically correct
  linear-light mode.
- Follow-up S029 work now renders Datoviz text, bounded 2D mesh, native colorbar, and S027
  transform/View2D rows as adapted, while axis guide contracts, explicit colorbar tick-label
  parity, colorbar query, mesh query, and public 3D promotion remain deferred pending focused S029
  audits.
