# M157 - S036 opaque depth fixture

## Stage

S036 - Static View3D, Orthographic Projection, and 3D Mesh Baseline

## Status

Completed.

## Summary

Establish the minimal strict 3D depth contract for opaque meshes.

## Deliverables

- Opaque nearer-fragment-wins fixture with unambiguous overlapping triangles.
- No-face-culling fixture with reversed winding still visible.
- Alpha-less-than-one negative/adapted fixture.
- Clipping-edge behavior documented as adapted or unsupported unless strict clipping is implemented.

## Stop Condition

Stop if strict depth cannot be implemented or reported without exposing backend depth-buffer state as
public protocol.

## Result

- Added Matplotlib 3D MeshVisual face ordering for opaque fixture triangles: projected faces are
  sorted far-to-near by average panel-NDC z so nearer faces are drawn last.
- Added regressions for nearer-face order, `depth_test=disabled` declared order, reversed winding
  visibility with no culling, and translucent 3D mesh rejection.
- Documented the boundary as an adapted face-order fixture, not strict fragment-depth support.
- Documented partially clipped 3D triangles as adapted/unverified until a strict clipping fixture is
  accepted.

Validation:

```bash
uv run pytest tests/test_view3d_protocol.py tests/test_mesh_visual_protocol.py tests/test_matplotlib_protocol_slice.py tests/test_import_surface.py -q
uv run ruff check src/gsp_matplotlib/protocol_renderer.py tests/test_matplotlib_protocol_slice.py
uv run mypy src/gsp_matplotlib/protocol_renderer.py --strict --show-error-codes
```
