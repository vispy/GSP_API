# M158 - S036 query ray readback

## Stage

S036 - Static View3D, Orthographic Projection, and 3D Mesh Baseline

## Status

Completed.

## Summary

Add strict `View3D` projection-inverse query context while keeping 3D visual picking deferred.

## Deliverables

- Query payload for panel logical xy, panel NDC xy, near/far DATA points, ray direction, view id,
  view revision, layout snapshot id, and view/projection snapshot id.
- Center and corner ray fixtures.
- Stale snapshot mismatch diagnostics.
- Structured unsupported result for 3D mesh hit/picking requests.

## Stop Condition

Stop if the query model starts requiring ray-triangle picking, depth-buffer readback, barycentric
attributes, or multi-hit stack semantics.

## Result

- Added `View3DQueryPayload` with payload kind `gsp.view3d-query@0.1` for projection-inverse ray
  readback.
- Added `unproject_view3d_panel_ndc_point()` and Matplotlib
  `query_view3d_ray_context()` for panel xy to near/far DATA ray context.
- Added center and corner ray fixtures plus stale layout/view-projection snapshot diagnostics.
- Kept `(N, 3)` `MeshVisual` picking deferred with `query_3d_visual_hit_deferred`.
- Updated query, View3D, and Matplotlib backend specs.

Validation:

```bash
uv run pytest tests/test_view3d_protocol.py tests/test_matplotlib_protocol_query.py tests/test_import_surface.py -q
uv run ruff check src/gsp/protocol/view3d.py src/gsp/protocol/query.py src/gsp/protocol/__init__.py src/gsp_matplotlib/protocol_query.py tests/test_view3d_protocol.py tests/test_matplotlib_protocol_query.py
uv run mypy src/gsp/protocol/ src/gsp_matplotlib/protocol_query.py --strict --show-error-codes
```
