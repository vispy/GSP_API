# M122 - S030 guide promotion and closeout

## Stage

S030 - Datoviz Guide Axis Proof

## Status

Completed.

## Summary

Close S030 by promoting or deferring Datoviz guide rows according to M120-M121 evidence.

## Deliverables

- Updated capability matrix policy only for proven guide rendering scopes.
- Regenerated review pack artifacts.
- Closeout notes documenting remaining guide query or layout gaps.

## Stop Condition

Stop if evidence is insufficient to classify guide rows without weakening the GSP semantic guide
contract.

## Outcome

Completed by local-main-codex. S030 is closed with Datoviz guide rows rendered as `adapted` review
artifacts, not promoted to `strict`.

Deliverables:

- Capability matrix policy now classifies rendered Datoviz guide rows as
  `datoviz_axis_guide_adapted_review`.
- Full S028 review suite regenerated for S030:
  `artifacts/visual_qa/s030/final-review-pack/index.md`.
- Closeout note added: `.agent/S030_CLOSEOUT.md`.
- Backend and visual QA specs updated to describe the S030 guide status.

Final review-pack status:

- All backend rows: `strict=52`, `adapted=6`, `unsupported=0`.
- Datoviz rows: `strict=23`, `adapted=6`, `unsupported=0`.
- `guide/view2d_auto_grid`: `adapted`.
- `guide/view2d_reversed_explicit`: `adapted`.

Remaining blockers:

- Panel title layout is unsupported because the Datoviz facade does not expose/prove panel title APIs.
- Guide and all-rendered guide query are unsupported.
- Strict guide parity remains deferred unless these semantics are proven or excluded by a future
  accepted guide-row contract.
