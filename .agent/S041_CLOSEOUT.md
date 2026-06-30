# S041 Closeout

## Result

S041 added a focused manual review pack for current public 3D behavior.

## Implemented

- Added `examples/review/11_view3d_lit_mesh_arcball.py`.
- Updated `examples/review/10_view3d_flat_lambert.py` wording after S040.
- Updated `examples/review/README.md` with 3D side-by-side review commands.
- Documented that Matplotlib provides the public arcball-style orbit/pan/zoom review path.
- Documented that Datoviz native `panel.arcball()` remains legacy/evidence-only, not public GSP
  semantics.

## Validation

- `uv run python examples/review/11_view3d_lit_mesh_arcball.py --backend matplotlib --offscreen --out-dir tmp/s041_lit_mesh_matplotlib`
- `uv run python examples/review/10_view3d_flat_lambert.py --backend matplotlib --offscreen --out-dir tmp/s041_lambert_matplotlib`
- `tools/compare-review-examples --offscreen examples/review/10_view3d_flat_lambert.py examples/review/11_view3d_lit_mesh_arcball.py`
- `uv run ruff check examples/review/10_view3d_flat_lambert.py examples/review/11_view3d_lit_mesh_arcball.py`
- `uv run python -m pytest tests/test_review_runner_interactive.py tests/test_datoviz_v04_protocol_renderer.py -q`

Local Datoviz offscreen review reported structured unsupported because the active binding is missing
`dvz_camera_desc` and `dvz_camera_set_orthographic_bounds`. This is a local runtime binding gap, not
a review-pack failure.

## Manual Commands

```bash
tools/compare-review-examples --live-side-by-side examples/review/10_view3d_flat_lambert.py
tools/compare-review-examples --live-side-by-side --interactive-navigation examples/review/11_view3d_lit_mesh_arcball.py
```

Use Matplotlib left-drag orbit, right/middle-drag pan, wheel zoom, and `r` reset for arcball-style
manual inspection.
