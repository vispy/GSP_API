# M164 - S037 Matplotlib navigation adapter

## Stage

S037 - Legacy 3D Reuse, Datoviz View3D Binding, and Public 3D Interaction

## Status

Completed by local-main-codex.

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

## Result

Completed. Added a private Matplotlib review-session adapter for S037 `View3D` navigation:
left-drag emits orbit actions, right/middle-drag emits pan actions, wheel emits zoom actions, and
`r` emits reset. The adapter applies canonical `View3DNavigationAction` values through
`apply_view3d_navigation_action()` and re-renders with the accepted canonical `View3D` result.

Validation performed:

```bash
uv run pytest tests/test_review_runner_interactive.py -q
uv run pytest tests/test_view3d_protocol.py tests/test_review_runner_interactive.py tests/test_import_surface.py -q
uv run ruff check examples/review/_review_runner.py tests/test_review_runner_interactive.py
uv run mypy src/gsp/protocol/view3d.py src/gsp/protocol/__init__.py --strict --show-error-codes
tools/compare-review-examples examples/review/07_view3d_cube.py --offscreen
```

`examples/review/_review_runner.py` is not part of the strict mypy target; a direct strict mypy run
on that example helper still reports pre-existing untyped example-module issues.
