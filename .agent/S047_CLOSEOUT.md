# S047 Closeout - Perspective View3D And Center-Dolly Zoom

## Result

S047 accepted perspective View3D as the default serious 3D projection direction and completed the
first implementation slice.

## Added

- `PerspectiveProjection3D` protocol model and projection snapshots.
- Matplotlib and Datoviz renderer support for perspective `View3D`.
- Perspective review examples for the main 3D mesh/material scenes.
- Center-dolly perspective zoom semantics for S037 `View3D` navigation.
- Matplotlib live review orbit/pan/zoom over perspective `View3D`.

## Boundary

- Perspective wheel zoom moves the camera eye along the camera-target line while preserving target,
  up, FOV, and near/far.
- Cursor-anchored perspective zoom remains deferred because it requires a layout/aspect-aware
  semantic decision.
- Datoviz live 3D navigation failed manual review and remains experimental opt-in only; normal
  review commands use static Datoviz View3D windows.
- S044 mesh triangle picking remains backend-neutral with Matplotlib CPU reference behavior;
  Datoviz still must not advertise `query.view3d.mesh_triangle_pick.v1`.

## Validation

- `uv run pytest tests/ -q`
- `uv run ruff check src tests examples`
- `uv run mypy src/ --strict --show-error-codes`
- `uv run python -m compileall -q src tests examples`
- Backend import smoke tests for Matplotlib and Datoviz.
- Offscreen review rendering for the changed perspective examples.
