# M098-S027 - Transform/view/camera scoping consultation

## Mission

M098

## Goal

Open S027 around transform, view, camera, navigation, and query-inverse semantics, and create the
ChatGPT Pro consultation packet required before implementation.

## Status

Completed.

## Deliverables

- Completed: Created `.agent/consultations/P012-transform-view-camera-navigation-semantics.md`.
- Completed: Recorded S027 as design-gated pending P012.
- Completed: Added open question Q100 for the ChatGPT Pro consultation result.
- Completed: Kept implementation blocked pending accepted ADR/spec baseline.

## Notes

- S027 should not implement transform/view/camera objects until P012 is answered.
- Likely dependent missions after P012: ADR/spec baseline, protocol dataclasses/validation,
  Matplotlib reference behavior, Datoviz capability gates, VisPy2 producer API, QA fixtures, and
  closeout.

## Validation

- `python -m json.tool .agent/status.json`
- `tools/agentctl brief`
- `tools/agentctl next`
- `git diff --check`
