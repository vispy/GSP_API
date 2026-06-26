# M107 - S028 reversed View2D tick and guide reference behavior

## Stage

S028 - Guide and View2D Integration

## Status

Draft.

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
