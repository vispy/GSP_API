# M167 - S037 Datoviz query ray readback parity

## Stage

S037 - Legacy 3D Reuse, Datoviz View3D Binding, and Public 3D Interaction

## Status

Completed for canonical ray-context payload generation.

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

## Completion

Completed by adding Datoviz-side canonical S036 ray-context generation:

- `gsp_datoviz.query.datoviz_query_view3d_ray_context()` returns
  `gsp.view3d-query@0.1` payloads from `QueryRequest`, `View3D`, and
  `View3DProjectionSnapshot`;
- `DatovizV04ProtocolRenderer.query_view3d_ray_context()` derives the current panel-local bounds
  and snapshot from the renderer's `View3D`;
- stale `layout_snapshot_id` / `view_snapshot_id` requests return
  `query_3d_snapshot_mismatch`;
- Datoviz capability snapshots advertise `query.view3d.ray_readback.v1` and `view3d-ray` only when
  the P022 camera binding is present.

The implementation intentionally does not claim Datoviz GPU visual hit picking for 3D meshes.
