# M107 - S028 reversed View2D tick and guide reference behavior

## Stage

S028 - Guide and View2D Integration

## Status

Completed.

## Summary

Implement deterministic tick resolution and Matplotlib guide rendering behavior for accepted
`View2D`, including reversed x/y ranges.

## Deliverables

- Update the deterministic tick resolver to accept reversed finite ranges according to M106 specs.
- Add focused tests for reversed auto and explicit tick behavior.
- Ensure Matplotlib guide rendering uses `View2D` limits for ticks and grids without relying on
  native locator semantics.

## Acceptance

- Focused tick and Matplotlib guide tests pass.
- Reversed `View2D` behavior is deterministic and matches spec.

## Stop Condition

Stop if tick ordering or grid semantics require a new layout/axis architecture decision.

## Result

- Updated `resolve_ticks()` to accept reversed finite ranges for auto ticks by resolving over the
  numeric interval spanned by the two limits.
- Preserved explicit tick values and labels exactly under reversed domains.
- Updated Matplotlib guide rendering to apply `View2D` x/y limits directly, including reversed
  limits.
- Added focused tests for reversed auto ticks, reversed explicit ticks, reversed guide rendering,
  and grid visibility under reversed limits.
- Validated focused and nearby guide/protocol/VisPy2 test slices.
