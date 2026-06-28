# M137 - S034 tiered review classification

## Stage

S034 - Resolved Layout and Guide Geometry Foundation

## Status

Completed by local-main-codex.

## Summary

Add the P016 review classification taxonomy to visual QA capability matrices without breaking the
older coarse `status` field.

## Deliverables

- `review_classification` per matrix row.
- `review_classification_taxonomy` and `review_classification_summary` in matrix output.
- Classification mapping for semantic strict passes, adapted review artifacts, native backend
  review, failures, and unsupported capabilities.
- Tests for Datoviz strict rows and adapted guide rows.

## Acceptance

- Existing `status` values remain unchanged.
- Adapted Datoviz guide rows classify as `review.adapted`.
- Existing strict rendered rows classify as `pass.semantic_strict`.
- Visual QA tests pass.

## Stop Condition

Stop before claiming `pass.layout_strict`; no backend currently emits enough review-pack evidence
for that classification.

## Result

Completed. The review pack can now report P016 classifications while preserving existing S029/S030
status behavior.
