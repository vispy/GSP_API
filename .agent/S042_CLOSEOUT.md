# S042 Closeout - Live Interactive Review Examples

## Summary

S042 completed the review-example interactivity pass.

## Completed

- Live review examples enable navigation by default for supported `View2D` and `View3D` scenes.
- Added `--no-interactive-navigation` to force static live review windows.
- Kept `--interactive-navigation` as a compatibility flag.
- Matplotlib review paths continue to use canonical S035/S037 action reducers.
- Datoviz `View2D` review paths use retained S035 navigation when live input bindings are available.
- Datoviz `View3D` now has an explicit `enable_gsp_view3d_navigation()` unsupported diagnostic.
- Docs and capability wording now describe the Datoviz `View3D` retained-navigation boundary.

## Datoviz View3D Boundary

The current Datoviz protocol renderer uploads 3D meshes as CPU-projected panel-NDC positions with
fixed controller mode. Updating only the native Datoviz camera does not move those retained buffers.
Reprojecting and reuploading mesh positions for every pointer event would not satisfy the retained
navigation boundary. Datoviz must not claim `view3d.navigation.orbit_pan_zoom.v1` until a native
DATA-space mesh path or another proven retained update strategy exists.

## Validation

Focused validation command:

```bash
PYTHONPATH=src .venv/bin/python -m pytest tests/test_review_runner_interactive.py tests/test_datoviz_v04_protocol_renderer.py::test_datoviz_view3d_live_navigation_reports_cpu_projected_mesh_boundary -q
```

Full validation should still run before release tagging.

## Follow-Up

If Datoviz gains a native DATA-space mesh path compatible with public `View3D`, reopen View3D live
navigation by implementing canonical S037 action application and retained camera/projection updates,
then prove no unchanged visual buffers are rebuilt or reuploaded.
