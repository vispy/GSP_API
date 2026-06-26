# M112 - S029 capability matrix and review-pack foundation

## Stage

S029 - Backend Capability Matrix and Visual Review Pack

## Status

Completed.

## Summary

Create the first post-S028 review-pack layer so Datoviz visual QA output is classified as strict,
adapted, experimental, unsupported, disabled, crashed, or not run before any broad capability
promotion.

## Deliverables

- Durable P013 response record.
- Visual QA capability matrix JSON and Markdown generation.
- Review-pack command over the existing S023-S028 visual QA runner.
- Datoviz runtime wrapper for local macOS review-pack generation.
- Focused tests for matrix taxonomy and review-pack artifacts.
- S029 Mission Control opening records.

## Acceptance

- Every selected case produces one Matplotlib row and one Datoviz row in the matrix.
- Matplotlib rendered rows are marked `strict`.
- Datoviz rendered rows are marked `adapted` until a family-specific promotion audit proves strict
  protocol conformance.
- Datoviz offscreen-disabled output is classified as `disabled`, not generic unsupported.
- Unsupported Datoviz output carries a reason code and promotion blocker.

## Stop Condition

Stop Datoviz promotion work if a family has no capability matrix row or if rendered output would be
promoted to strict without documented semantic evidence.

## Result

- Added `gsp.qa.visual.capability_matrix` and `gsp.qa.visual.review_pack`.
- Added `python -m gsp.qa.visual review-pack`.
- Added `tools/run_datoviz_visual_review_pack.sh`.
- Updated visual QA harness docs with S029 review-pack workflow.
- Archived the P013 ChatGPT Pro response in `.agent/consultations/P013-response.md`.
