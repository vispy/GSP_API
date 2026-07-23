# M276 - S065 retained and live camera behavior

## Status

Draft; promote after M275. Target repositories: `gsp`, `vispy2`.

## Goal

Make programmatic and interactive View3D camera changes reliable, retained, capability-declared,
and ready for human review.

## Work

- Wire Datoviz sessions to enable View3D navigation for accepted 3D scenes.
- Remove the experimental capability gate only if current bindings and automated lifecycle evidence
  pass; otherwise keep it unadvertised and produce a precise blocker.
- Prove orbit/pan/zoom/reset change canonical View3D state and captured output while unchanged
  visual buffers are not re-uploaded.
- Add deterministic Matplotlib re-render/update coverage from revised View3D state.
- Add a VisPy2 live camera example with explicit caller-owned session lifecycle.
- Run isolated repeated create/display/update/close cycles and callback cleanup checks.

## Locks

- `gsp`: backend sessions, navigation bindings/capabilities/tests
- `vispy2`: camera display example and focused tests

## Acceptance

Programmatic camera changes pass both backends. Datoviz passes at least 25 isolated lifecycle
iterations with zero crash/hang and exact callback cleanup. A live review command and expected
controls are recorded for the owner. Capability advertisement matches evidence.

## Human checkpoint

If the Datoviz live capability is promoted, pause for owner interaction review before M277.

## Stop conditions

Stop on native crash, callback leak, full visual re-upload for camera-only changes, hidden
thread/event-loop ownership, or a need to edit Datoviz.

