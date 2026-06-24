# M096-S026 - S026 VisPy2 color mapping producer API

## Mission

M096

## Goal

Add VisPy2 producer APIs for accepted S026 color mapping/colorbar/scalar behavior.

## Status

Completed.

## Deliverables

- Completed: High-level VisPy2 API additions matching M091.
- Completed: Example that emits formal GSP protocol scenes.
- Completed: Focused producer tests.

## Notes

- Added VisPy2 producer methods for `color_scale()` and `colorbar()`.
- `imshow()` can link scalar images to an explicit S026 color scale through `color_scale` or `cmap` plus `clim`.
- `scatter()` and `markers()` can emit point color and marker fill `ScalarColorEncoding` payloads.
- `Figure` now exposes `color_scales()` and `colorbar_guides()` and passes color scales to the Matplotlib reference renderer.
- Added `examples/vispy2_protocol_color_mapping.py` and focused tests in `tests/test_vispy2_protocol_mvp.py`.

## Acceptance

- M091 baseline exists.
- API does not expose backend draw calls, Matplotlib internals, or Datoviz shader/slot details.

## Stop Conditions

- Stop if API shape requires semantics not accepted by M091.
