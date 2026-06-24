# M093-S026 - S026 Matplotlib color mapping reference behavior

## Mission

M093

## Goal

Add Matplotlib reference rendering/query behavior for the accepted S026 color mapping slice.

## Status

Completed.

## Deliverables

- Completed: Reference rendering for accepted scalar/color mapping behavior.
- Completed: Query/readback support matching M091.
- Completed: Focused Matplotlib tests.

## Notes

- Added canonical scalar-to-RGBA LUT sampling helpers for Matplotlib reference paths.
- Wired scalar color scales into ImageVisual, PointVisual, and MarkerVisual rendering.
- Added scalar color query payloads for image texels, points, and markers.
- Kept MeshVisual scalar face colors capability-gated for a later backend-specific mission.

## Acceptance

- M091 and relevant protocol validation are completed first.
- Behavior is documented and capability-gated where needed.

## Stop Conditions

- Stop if behavior depends on backend-specific Matplotlib semantics not accepted by M091.
