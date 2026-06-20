# M003 - Matplotlib point/image reference slice

## Goal

Make the Matplotlib backend consume the first formal GSP point and image models.

## State

Completed in the current Codex session.

## Expected tasks

- VIS-POINT-001: finalize first point visual schema.
- VIS-IMAGE-001: finalize first image visual schema.
- MPL-POINT-001: render point visual from new model.
- MPL-IMAGE-001: render image visual from new model.
- CONF-POINT-001: add point fixture/test.
- CONF-IMAGE-001: add image fixture/test.

## Legacy inputs

- `LEGACY_MAP.md`
- `src/gsp_matplotlib/renderer/matplotlib_renderer.py`
- `src/gsp_matplotlib/renderer/matplotlib_renderer_points.py`
- `src/gsp_matplotlib/renderer/matplotlib_renderer_image.py`
- `examples/points_example.py`
- `examples/image_example.py`
- `examples/expected/`

## Scope guard

Keep Matplotlib as the reference/conformance backend. Prefer narrow fixtures over broad example-suite rewrites.

## Stop conditions

Stop if image coordinate semantics or vector export semantics require architecture decisions.

## Result

- Added first formal protocol visual models: `PointVisual` and `ImageVisual`.
- Added explicit `ImageOrigin` and `ImageInterpolation` fields for the image reference slice.
- Added `gsp_matplotlib.protocol_renderer` for direct Matplotlib rendering of the formal models.
- Added focused conformance tests for point and image artists.
- Left the legacy `MatplotlibRenderer` and examples unchanged.
