# M093 - S026 Matplotlib color mapping reference behavior

## Stage

S026 - Color Mapping, Colorbars, and Scalar Data Semantics

## Status

Completed.

## Summary

Implement Matplotlib reference behavior for accepted S026 color mapping/query semantics.

## Planned Deliverables

- Completed: Reference rendering and query/readback updates.
- Completed: Focused tests and docs notes.

## Outcome

Matplotlib now has deterministic S026 scalar color reference behavior for scalar
images, point colors, marker fill colors, semantic colorbar guides, and query
payload readback. Mesh scalar face colors remain capability-gated.

## Acceptance

- M091/M092 prerequisites are complete.
- Matplotlib behavior matches accepted conformance semantics.

## Stop Condition

Stop if reference behavior would exceed accepted S026 scope.
