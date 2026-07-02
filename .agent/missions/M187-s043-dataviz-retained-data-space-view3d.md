# M187 - S043 Datoviz retained DATA-space View3D visuals

## Stage

S043 - Datoviz Panel Frame, Guide Strictness, And Retained View3D

## Status

Completed.

## Summary

Implement Datoviz retained DATA-space `View3D` visual attachments and retained update instrumentation
needed for strict live orbit/pan/zoom.

## Deliverables

- Added `view3d.retained_data_space_visuals.v1` as a separate capability from full live
  orbit/pan/zoom navigation.
- Added a Datoviz retained DATA-space 3D mesh path gated on the revisioned panel `View3D`
  descriptor/state APIs (`DvzPanelView3DDesc`, `DvzPanelView3DState`,
  `dvz_panel_set_view3d_desc()`, `dvz_panel_view3d_state()`, and related camera readback/update
  symbols).
- Added retained View3D update stats for vertex uploads, index uploads, visual rebuilds,
  view/projection uniform updates, and snapshot resolves.
- Added retained camera/projection update and state readback helpers that avoid rewriting unchanged
  mesh vertex/index buffers.
- Added fake-facade GSP tests for DATA-space mesh upload, visual identity stability, no buffer
  reupload during retained camera updates, state readback, and ray/query snapshot equality.
- Updated Datoviz backend capability docs to distinguish retained DATA-space visuals from M188 live
  navigation.

## Acceptance

- Camera/projection changes update retained View3D state without vertex/index buffer writes.
- Mesh visual identity remains stable across retained View3D updates.
- Ray/query state uses the same layout and view/projection snapshot ids as retained state readback.

## Boundary Note

This mission was completed on the GSP_API side only. The external Datoviz checkout was read for API
shape (`dvz_panel_set_view3d_desc()`, `dvz_panel_view3d_state()`, `dvz_panel_camera()`, camera
view/projection readback/update symbols) but not modified.

## Validation

- `uv run pytest tests/test_datoviz_v04_protocol_renderer.py -q`
- `uv run pytest tests/ -q`
- `uv run mypy src/ --strict --show-error-codes`
- `uv run ruff check src tests`
- `GSP_BACKEND=matplotlib uv run python -c "import gsp; print('Matplotlib backend OK')"`
- `GSP_BACKEND=datoviz uv run python -c "import gsp; print('DatoViz backend OK')"`
- `git diff --check`

## Stop Conditions

- Stop if ordinary camera updates require CPU vertex reprojection.
- Stop if unchanged visual buffers are reuploaded during ordinary navigation.
- Stop if visual identity changes during navigation.
- Stop if query/ray state diverges from render state.
