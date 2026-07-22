# M268 - S063 Matplotlib canonical live View2D synchronization

## Stage

S063 - Live View2D Interaction Parity And Regression Safety

## Status

Approved; M267 completed and the project owner authorized sequential execution.

## Summary

Keep DATA visuals in Matplotlib data coordinates, preserve NDC placement, and synchronize native
toolbar limit changes into session-owned canonical `View2D` state without recursive callbacks.

## Acceptance

- All supported 2D DATA visual families move with the grid; NDC overlays remain fixed.
- Initial static rendering, reversed ranges, affine transforms, guide layout, and queries retain
  accepted semantics.
- Toolbar changes update canonical ranges, revision, and snapshot identity.
- Programmatic canonical updates do not recurse and callback cleanup is deterministic.
- Focused tests, the full Matplotlib suite, strict mypy, and Ruff pass.

## Stop conditions

Stop on unexplained static-output changes, stale query/layout claims, producer state leakage, or a
need for an unreviewed public API change.
