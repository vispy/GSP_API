# M149 - S035 navigation numeric fixtures

## Stage

S035 - Retained View2D Navigation and Pan/Zoom

## Status

Completed by local-main-codex.

## Summary

Add deterministic fixtures for navigation actions independent of GUI event systems.

## Deliverables

- Initial `View2D` + resolved panel rectangle + action sequence fixtures.
- Expected resulting `View2D` revisions for pan, zoom-about-anchor, reset, and set-view.
- Negative fixtures for non-finite deltas, invalid zoom factors, stale revisions, and stale layout
  snapshots.
- Tests that do not require a live display.

## Stop Condition

Stop if fixture semantics conflict with S027 `View2D` or S034 resolved-layout snapshot rules.

## Result

Completed. Added deterministic `pan_view2d()` and `zoom_view2d_about()` helpers over `View2D` and
`LogicalPixelRect`, including reversed-limit behavior and invalid panel-rectangle diagnostics.
Extended focused tests with pan, zoom-anchor, reversed-limit, and invalid-rect fixtures.

Validation performed:

- `uv run python -m py_compile src/gsp/protocol/navigation.py src/gsp/protocol/__init__.py tests/test_navigation_protocol.py`
- `uv run ruff check src/gsp/protocol/navigation.py src/gsp/protocol/__init__.py tests/test_navigation_protocol.py`
- `uv run pytest tests/test_navigation_protocol.py -q`
- `uv run mypy src/gsp/protocol/ --strict --show-error-codes`
- `uv run pytest tests/ -q` (`453 passed, 3 skipped`)
