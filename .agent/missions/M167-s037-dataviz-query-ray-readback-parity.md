# M167 - S037 Datoviz query ray readback parity

## Stage

S037 - Legacy 3D Reuse, Datoviz View3D Binding, and Public 3D Interaction

## Status

Draft, pending M165.

## Summary

Add or verify Datoviz `query.view3d.ray_readback.v1` only if public `View3D` snapshot parity is
available.

## Deliverables

- Query payload generation from canonical snapshots.
- Snapshot mismatch diagnostics.
- Parity tests against Matplotlib/S036 CPU math.
- Capability-gated Datoviz query support wording.

## Acceptance

- Datoviz query payload fields match S036 semantics, or the capability remains unclaimed.

## Stop Condition

Stop if query payloads cannot be tied to canonical `View3D` revision and projection snapshot ids.
