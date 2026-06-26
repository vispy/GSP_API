# M101-S027 - Matplotlib transform/view reference behavior

## Mission

M101

## Goal

Add strict Matplotlib/reference rendering and query inverse behavior for the accepted S027 2D affine
transform and `View2D` subset.

## Status

Completed.

## Deliverables

- Apply visual-local affine transforms to accepted positional visual families.
- Map DATA visuals through `View2D` and leave NDC visuals independent of `View2D`.
- Preserve screen-pixel sizes, stroke widths, text font sizes, marker glyphs, and scalar color
  semantics.
- Emit transformed query inverse payloads for strict reference query paths.
- Add focused tests for transformed render/query cases and reversed limits.

## Acceptance

- Focused Matplotlib render/query tests pass.
- Existing visual-family and query tests remain green.
- Query payload fields agree with `spec/transforms.md`.

## Stop Conditions

- Stop on any need for equal-aspect/layout, arbitrary image affine, 3D camera/projection, depth, or
  transform graph semantics.

## Completion Notes

- Implemented strict Matplotlib transform/view reference helpers and optional renderer/query
  parameters.
- Preserved existing behavior when no S027 view/transform context is supplied, except for equivalent
  internal text position normalization.
- Validation: full `uv run pytest tests/` passed with 357 passed and 8 skipped; backend import smoke
  passed; mypy still reports five pre-existing unrelated errors outside M101 scope.
