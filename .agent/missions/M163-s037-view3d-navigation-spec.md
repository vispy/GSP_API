# M163 - S037 View3D navigation spec

## Stage

S037 - Legacy 3D Reuse, Datoviz View3D Binding, and Public 3D Interaction

## Status

Ready.

## Summary

Implement the accepted public `View3D` navigation protocol model from `spec/view3d_navigation.md`
without binding it to Matplotlib or Datoviz.

## Deliverables

- `View3DNavigationAction` and payload dataclasses.
- `View3DNavigationResult`.
- Navigation diagnostics.
- Pure reducer functions for orbit, pan, zoom, set-camera, set-projection, and reset.
- Tests for revision freshness, snapshot mismatch rejection, invalid deltas, invalid zoom, invalid
  results, and deterministic projection snapshot changes.

## Acceptance

- Navigation can be tested without Matplotlib or Datoviz.
- Accepted actions produce new canonical `View3D` state and fresh projection snapshot ids.
- Stale actions are rejected rather than silently rebased.

## Stop Condition

Stop if implementation would require backend-native controllers, perspective projection, public
matrix-first authoring, or material/light/texture semantics.
