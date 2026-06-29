# M151 - S035 Datoviz retained View2D proof

## Stage

S035 - Retained View2D Navigation and Pan/Zoom

## Status

Draft.

## Summary

Prove that Datoviz pan/zoom can update retained panel/view/projection state without re-uploading
unchanged visual geometry buffers.

## Deliverables

- Instrumented Datoviz v0.4 protocol-renderer test or fake-facade proof.
- Pan/zoom path calls `dvz_panel_set_domain`, `dvz_panel_set_view2d`, or equivalent retained
  view/uniform update APIs.
- Pan/zoom path does not call `dvz_visual_set_data`, image upload, index upload, or visual recreation
  for unchanged point/image/mesh data.
- Capability metadata distinguishes retained fast path from CPU-remap/adapted fallbacks.
- Large-scene smoke target or benchmark hook suitable for later live review.

## Stop Condition

Stop if Datoviz v0.4 lacks a retained view/uniform update path; report the blocker rather than
silently falling back to CPU remapping for the strict interactive path.
