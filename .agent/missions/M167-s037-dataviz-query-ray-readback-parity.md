# M167 - S037 Datoviz query ray readback parity

## Stage

S037 - Legacy 3D Reuse, Datoviz View3D Binding, and Public 3D Interaction

## Status

Deferred, pending M166 Datoviz retained View3D render support.

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
- `query.view3d.ray_readback.v1` remains unavailable until M166 has proven strict Datoviz
  `view3d.static.orthographic.v1` and `meshvisual.positions3d.data.view3d.v1` support.

## Stop Condition

Stop if query payloads cannot be tied to canonical `View3D` revision and projection snapshot ids.

## Source

`.agent/consultations/P022-response.md`.
