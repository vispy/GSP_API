# M167 - S037 Datoviz query ray readback parity

## Stage

S037 - Legacy 3D Reuse, Datoviz View3D Binding, and Public 3D Interaction

## Status

Unblocked by M166; implementation in progress.

## Summary

Add or verify Datoviz `query.view3d.ray_readback.v1` only if public `View3D` snapshot parity is
available. P022 explicitly keeps Datoviz ray readback out of scope for the camera binding and
orthographic-bounds upgrade.

## Deliverables

- Query payload generation from canonical snapshots.
- Snapshot mismatch diagnostics.
- Parity tests against Matplotlib/S036 CPU math.
- Capability-gated Datoviz query support wording.

## Acceptance

- Datoviz query payload fields match S036 semantics, or the capability remains unclaimed.
- `query.view3d.ray_readback.v1` may be claimed only for canonical ray-context payload generation.
  GPU visual hit picking remains outside this mission unless a separate Datoviz readback proof is
  added.

## Stop Condition

Stop if query payloads cannot be tied to canonical `View3D` revision and projection snapshot ids.

## Source

`.agent/consultations/P022-response.md`.
