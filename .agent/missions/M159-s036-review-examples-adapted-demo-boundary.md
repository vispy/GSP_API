# M159 - S036 review examples and adapted demo boundary

## Stage

S036 - Static View3D, Orthographic Projection, and 3D Mesh Baseline

## Status

Completed.

## Summary

Add user-facing examples that demonstrate useful static 3D behavior without promoting public 3D
navigation semantics.

## Deliverables

- Static cube mesh example.
- Simple terrain-like mesh example.
- NDC-depth triangle example.
- Opaque overlap/depth example.
- Alpha-not-strict negative/adapted example.
- Optional adapted interactive demo that emits canonical `View3D` replacements, clearly documented
  as non-public navigation semantics.

## Stop Condition

Stop if examples require public `View3DNavigationController`, perspective, materials/lights, or
backend-native controller objects.

## Result

- Added `ReviewScene.view3d` and routed it only into Matplotlib MeshVisual rendering.
- Added numbered static S036 review examples:
  - `07_view3d_cube.py`;
  - `08_view3d_terrain.py`;
  - `09_view3d_ndc_depth.py`.
- Added non-default `s036_alpha_not_strict_negative.py` to verify the
  `mesh3d_alpha_not_strict` diagnostic without making the default numbered review sweep fail.
- Documented that S036 View3D examples are static and do not introduce public 3D navigation.

Validation:

```bash
uv run python examples/review/07_view3d_cube.py --backend matplotlib --offscreen --out-dir artifacts/example_review/check_07_view3d_cube
uv run python examples/review/08_view3d_terrain.py --backend matplotlib --offscreen --out-dir artifacts/example_review/check_08_view3d_terrain
uv run python examples/review/09_view3d_ndc_depth.py --backend matplotlib --offscreen --out-dir artifacts/example_review/check_09_view3d_ndc_depth
uv run python examples/review/s036_alpha_not_strict_negative.py
tools/compare-review-examples examples/review/07_view3d_cube.py examples/review/08_view3d_terrain.py examples/review/09_view3d_ndc_depth.py --offscreen
uv run ruff check examples/review/_review_runner.py examples/review/07_view3d_cube.py examples/review/08_view3d_terrain.py examples/review/09_view3d_ndc_depth.py examples/review/s036_alpha_not_strict_negative.py tests/test_review_runner_interactive.py
uv run pytest tests/test_review_runner_interactive.py -q
```
