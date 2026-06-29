# M147 - S035 navigation ADR/spec baseline

## Stage

S035 - Retained View2D Navigation and Pan/Zoom

## Status

Completed by local-main-codex.

## Summary

Convert the P019 response and the user-approved performance model into an accepted ADR and spec for
`View2D` navigation actions.

## Deliverables

- ADR for `View2D` navigation controller v1.
- `spec/navigation.md` or equivalent spec section covering `pan_by`, `zoom_about`, `set_view`, and
  `reset_view`.
- SPEC_INDEX update.
- Explicit performance requirement: retained GPU backends must implement pan/zoom through panel
  view/projection or data-to-clip uniform/state updates, not visual geometry re-upload, when visual
  data are unchanged.
- Explicit distinction between public semantic actions and backend-native event adapters.
- Query/readback coherence requirements for `view2d_revision`, `view_snapshot_id`, and
  `layout_snapshot_id`.

## Acceptance

- The ADR/spec preserve `View2D` as the public semantic state.
- Raw mouse, wheel, keyboard, touch, and backend controller objects remain deferred public protocol.
- The Datoviz fast path requirement is testable by later missions.
- Existing S027 transform semantics are referenced rather than replaced.

## Stop Condition

Stop if the spec requires public 3D camera semantics, a general event propagation model, or
backend-native controller APIs.

## Result

Completed. Added ADR-0022, `spec/navigation.md`, S035 decision notes, SPEC_INDEX entries, and the
S035 protocol-spec pointer. The accepted baseline keeps `View2D` as the public semantic state,
defines deterministic navigation actions, keeps native input events as backend adapters, and records
the retained-GPU performance requirement for Datoviz and similar backends.
