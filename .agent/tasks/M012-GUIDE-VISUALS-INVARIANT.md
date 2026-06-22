# M012-GUIDE-VISUALS-INVARIANT - Keep guides out of Figure.visuals()

## Mission

M012

## Goal

Preserve the invariant that `Figure.visuals()` returns user data visuals only.

## Expected output

- Tests covering guide/tick preparation alongside VisPy2 point/image visuals.
- No generated guide, axis, tick, label, grid, or title objects appended to `Figure.visuals()`.

## Acceptance

- Existing VisPy2 MVP behavior remains intact.
- New guide/tick resolver work does not mutate user visual lists.

## Stop conditions

Stop if implementation requires generated guide primitives to appear in `Figure.visuals()`.

