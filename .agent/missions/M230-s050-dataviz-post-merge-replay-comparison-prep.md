# M230 - S050 Datoviz post-merge replay comparison prep

## Stage

S050 - Post-S048 Implementation Roadmap And Datoviz Mesh-Pick Evidence

## Status

Completed by local-main-codex.

## Summary

Prepare a repeatable GSP-side replay and comparison path for the Datoviz pre-RC API cleanup branch
after it lands or materially changes, without editing Datoviz or changing capability advertisement.

## Required Context

- `.agent/S050_DATOVIZ_PRE_RC_COMPATIBILITY_REVIEW.md`
- `artifacts/visual_qa/s050/pre_rc_compat_s028_timeout/`
- `src/gsp/qa/visual/review_pack.py`
- `src/gsp/qa/visual/capability_matrix.py`
- `tools/datoviz_v04_smoke.py`
- `tools/probe_datoviz_guide_axis.py`

## Deliverables

- Add a capability-matrix comparison command for review-pack baseline/candidate checks.
- Add a replay wrapper that runs smoke, guide probe, S028 Datoviz offscreen review pack, and matrix
  comparison against the committed pre-RC baseline.
- Add focused tests for improvement/regression classification.
- Record Mission Control handoff and keep M222 blocked.

## Acceptance

- Focused comparison/review-pack tests pass.
- CLI self-comparison of the committed pre-RC baseline succeeds.
- `tools/agentctl next` still reports M222 blocked.

## Stop Conditions

- Stop before editing the sibling Datoviz repository.
- Stop before advertising Datoviz Texture2D renderer capabilities.
- Stop before treating a crash reduction as a capability promotion without fresh review.

## Result

Completed locally. See `.agent/S050_DATOVIZ_POST_MERGE_REPLAY_PREP.md`.

New entry points:

- `python -m gsp.qa.visual compare-matrix`
- `tools/run_datoviz_pre_rc_replay.sh`

M222 remains blocked.
