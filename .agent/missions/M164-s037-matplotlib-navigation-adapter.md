# M164 - S037 Matplotlib navigation adapter

## Stage

S037 - Legacy 3D Reuse, Datoviz View3D Binding, and Public 3D Interaction

## Status

Draft, pending M163.

## Summary

Wire accepted public `View3D` navigation actions to Matplotlib review interaction without exposing
Matplotlib objects as public API.

## Deliverables

- Matplotlib review adapter for orbit, pan, zoom, reset, set-camera, and set-projection where
  accepted.
- Interactive example or review runner path that emits canonical actions and consumes canonical
  results.
- Query/snapshot freshness tests after navigation.

## Acceptance

- Interactions produce canonical `View3D` revisions and fresh projection snapshots.
- Matplotlib callback ids, axes, and artists remain private.

## Stop Condition

Stop if interaction cannot be expressed through accepted `View3DNavigationAction` values.
