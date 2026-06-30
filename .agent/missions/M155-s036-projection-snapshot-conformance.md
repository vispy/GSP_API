# M155 - S036 projection and snapshot conformance

## Stage

S036 - Static View3D, Orthographic Projection, and 3D Mesh Baseline

## Status

Completed by local-main-codex.

## Summary

Implement backend-independent orthographic projection math and snapshot identity for `View3D`.

## Deliverables

- Deterministic camera basis derivation.
- DATA-to-camera and camera-to-NDC projection helpers.
- View/projection snapshot identity fields.
- Numeric fixtures for canonical basis, cube projection, reversed x/y bounds, and off-axis bounds.
- Tests proving projection math is independent of raster backend.

## Stop Condition

Stop if projection conventions are ambiguous or if a backend-specific clip/depth convention leaks into
the public protocol.

## Result

Completed. Added deterministic `View3D` DATA-point projection, derived projection snapshots, stable
view/projection snapshot ids, and numeric fixtures for canonical cube projection, reversed x/y
bounds, off-axis bounds, and snapshot identity changes.

Validation performed:

- `uv run pytest tests/test_view3d_protocol.py tests/test_transform_protocol.py tests/test_navigation_protocol.py -q`
- `uv run ruff check src/gsp/protocol/view3d.py src/gsp/protocol/__init__.py tests/test_view3d_protocol.py`
- `uv run mypy src/gsp/protocol/ --strict --show-error-codes`
