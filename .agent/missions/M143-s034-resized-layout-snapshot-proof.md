# M143 - S034 resized layout snapshot proof

## Stage

S034 - Resolved Layout and Guide Geometry Foundation

## Status

Completed by local-main-codex.

## Summary

Add a focused visual QA proof that Matplotlib resolved layout snapshots track resized render
targets.

## Deliverables

- Test coverage running the S034 scatter/title/axis/grid layout fixture at two output resolutions.
- Assertions that `render_target.logical_width_px`, `render_target.logical_height_px`, and
  `plot_rect_px` update with the rendered viewport.
- Assertions that `grid_clip_rect_px` remains equal to `plot_rect_px` at both sizes.

## Acceptance

- The resized viewport proof passes through the visual QA runner.
- The proof uses the Matplotlib layout snapshot metadata recorded in M142.
- No backend is promoted to full `layout_strict`.

## Stop Condition

Stop before adding non-1.0 device-scale semantics or Datoviz-native layout proofs without a concrete
render-target/device-scale contract.

## Result

Completed. S034 QA now verifies that Matplotlib layout snapshot metadata changes with resized
logical render targets.
