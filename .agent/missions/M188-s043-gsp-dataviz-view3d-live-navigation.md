# M188 - S043 GSP Datoviz View3D live navigation

## Stage

S043 - Datoviz Panel Frame, Guide Strictness, And Retained View3D

## Status

Completed.

## Summary

Enable Datoviz `View3D` live navigation in GSP review paths behind retained DATA-space capability
gates.

## Deliverables

- Added Datoviz `view3d.navigation.orbit_pan_zoom.v1` promotion only when live input and retained
  DATA-space `View3D` symbols are both available.
- Added renderer-level canonical `View3DNavigationAction` replay into retained Datoviz camera and
  orthographic projection state.
- Added Datoviz retained-state readback checks against canonical GSP camera/projection state.
- Added live pointer input handling for left-drag orbit, right-drag pan, wheel zoom, and
  double-click reset.
- Added tests proving unchanged mesh vertex/index buffers and visual identity are preserved during
  ordinary live `View3D` navigation.
- Added ray readback proof after retained live navigation using the same layout/projection snapshot
  ids.
- Updated review-runner behavior and documentation to enable Datoviz live `View3D` navigation behind
  capability gates while preserving static fallback diagnostics.

## Acceptance

- `view3d.navigation.orbit_pan_zoom.v1` is advertised only when retained navigation and live input
  are available.
- Live Datoviz `View3D` review examples enable navigation only behind capability gates.
- Static fallback diagnostics remain clear for older Datoviz builds.
- Orbit, pan, zoom, and reset update retained camera/projection state without unchanged mesh buffer
  reuploads.

## Validation

- `uv run pytest tests/test_datoviz_v04_protocol_renderer.py -q`
- `uv run pytest tests/test_review_runner_interactive.py -q`
- `uv run pytest tests/ -q --cov=src --cov-report=term-missing` (`562 passed, 2 skipped`, total
  coverage 64%)
- `uv run mypy src/ --strict --show-error-codes`
- `uv run ruff check src tests examples/review`
- `GSP_BACKEND=matplotlib uv run python -c "import gsp; print('Matplotlib backend OK')"`
- `GSP_BACKEND=datoviz uv run python -c "import gsp; print('DatoViz backend OK')"`
- `git diff --check`

## Stop Conditions

- Stop if Datoviz controller effects cannot be synchronized to canonical GSP state.
- Stop if unchanged visual buffers are reuploaded during ordinary navigation.
- Stop if GSP would have to expose Datoviz controller names publicly.
