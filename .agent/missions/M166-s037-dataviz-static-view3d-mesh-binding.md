# M166 - S037 Datoviz static View3D mesh binding

## Stage

S037 - Legacy 3D Reuse, Datoviz View3D Binding, and Public 3D Interaction

## Status

Deferred, pending Datoviz camera binding and orthographic-bounds API.

## Summary

Implement the Datoviz retained `(N, 3)` `MeshVisual` path only if M165 proves a safe public
`View3D` lowering path and P022's Datoviz-side prerequisites are present.

P022 concluded that a binding-only upgrade is necessary but not sufficient for strict GSP
`view3d.static.orthographic.v1`. M166 must not start until Datoviz exposes both safe Python camera
ctypes layouts and a camera-level explicit orthographic-bounds setter.

Required Datoviz-side prerequisites:

- `DvzCameraView` exposes ABI-valid Python fields `eye`, `target`, and `up`.
- `DvzCameraDesc` exposes ABI-valid Python fields `view` and `projection`.
- `dvz_camera_view()` and `dvz_camera_desc()` are emitted only after their by-value return layouts
  are ABI-valid.
- `dvz_camera_set_orthographic_bounds(camera, left, right, bottom, top, near, far)` is public and
  bindable from Python.
- Explicit bounds mode accepts ordered GSP bounds directly, including reversed x/y bounds, and
  resize does not rewrite explicit world-space bounds.
- Existing centered `dvz_camera_set_orthographic(height, near, far)` behavior remains compatible.

## Deliverables

- Private `DatovizView3DAdapter` or equivalent lowering layer.
- DATA and NDC3 lowering paths.
- Direct lowering from `OrthographicProjection3D.xlim`, `.ylim`, and `.near_far` to Datoviz
  orthographic bounds.
- Color/index upload and depth-mode mapping.
- Capability gates and diagnostics.
- Focused tests for unsupported binding, missing `View3D`, transform rejection, alpha rejection,
  DATA projection, NDC3 interpretation, off-axis/reversed bounds, and depth evidence.

## Acceptance

- Datoviz renders accepted `(N, 3)` examples without z flattening before claiming support.
- Centered, off-axis, reversed-x, reversed-y, and both-reversed orthographic cases match canonical
  GSP projection snapshots.
- Unsupported environments keep structured `mesh3d_coordinate_space_unsupported` diagnostics.
- Older Datoviz builds without `dvz_camera_set_orthographic_bounds` remain unsupported.

## Stop Condition

Stop if Datoviz lacks the P022 camera-level orthographic-bounds API or if retained Datoviz rendering
cannot prove public GSP `View3D` semantics.

## Source

`.agent/consultations/P022-response.md`.
