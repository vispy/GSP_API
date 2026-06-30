# M156 - S036 MeshVisual `(N, 3)` DATA/NDC rendering path

## Stage

S036 - Static View3D, Orthographic Projection, and 3D Mesh Baseline

## Status

Completed.

## Summary

Make `(N, 3)` `MeshVisual` renderable where a backend advertises the S036 3D capabilities.

## Deliverables

- `(N, 3)` DATA interpretation through `View3D`.
- `(N, 3)` NDC interpretation as panel NDC plus depth.
- Structured unsupported diagnostics for missing `View3D` or missing backend support.
- Datoviz retained rendering path if v0.4 bindings support it, otherwise a documented unsupported
  report with exact blocker evidence.
- Regression tests proving existing `(N, 2)` mesh behavior is unchanged.

## Stop Condition

Stop if Datoviz implementation requires public backend-native camera/draw-state names or if support
would silently flatten z.

## Result

- Added Matplotlib reference projection support for `(N, 3)` `MeshVisual` DATA vertices through
  explicit `View3D`, and NDC vertices as panel NDC3.
- Preserved existing `(N, 2)` MeshVisual behavior and kept 2D affine transforms unsupported for
  `(N, 3)` geometry with `mesh3d_transform_unsupported`.
- Kept Datoviz retained v0.4 MeshVisual support bounded to 2D and added the
  `mesh3d_coordinate_space_unsupported` diagnostic for public `(N, 3)` inputs until a View3D camera
  binding exists.
- Updated backend specs and focused Matplotlib/Datoviz regression tests.

Validation:

```bash
uv run pytest tests/test_view3d_protocol.py tests/test_mesh_visual_protocol.py tests/test_matplotlib_protocol_slice.py tests/test_datoviz_v04_protocol_renderer.py::test_add_mesh_visual_accepts_default_data_domain_and_rejects_3d_with_diagnostic tests/test_import_surface.py -q
uv run ruff check src/gsp/protocol/__init__.py src/gsp_matplotlib/protocol_renderer.py src/gsp_datoviz/protocol_renderer.py tests/test_matplotlib_protocol_slice.py tests/test_datoviz_v04_protocol_renderer.py
uv run mypy src/gsp/protocol/ src/gsp_matplotlib/protocol_renderer.py src/gsp_datoviz/protocol_renderer.py --strict --show-error-codes
```
