# M182 - S043 Datoviz panel frame snapshot core

## Stage

S043 - Datoviz Panel Frame, Guide Strictness, And Retained View3D

## Status

Ready.

## Summary

Implement the Datoviz core `DvzPanelFrameSnapshot` architecture needed by both guide strictness and
retained View3D navigation.

## Deliverables

- Datoviz design note committed in the Datoviz repo, derived from
  `.agent/DATOVIZ_PANEL_FRAME_ARCHITECTURE.md`.
- C API for resolving, inspecting, retaining, and releasing immutable panel frame snapshots.
- Snapshot ids and panel/layout/view/guide/visual revisions.
- Panel rect, plot rect, grid clip rect, logical size, framebuffer size, and device scale.
- View transform fields sufficient for View2D and View3D query/readback.
- Diagnostics for unavailable fields.
- Python wrapper/binding exposure for the snapshot core.
- Native Datoviz tests for snapshot identity, invalidation, resize, device scale, and existing grid
  clipping behavior.

## Acceptance

- Render-affecting panel/plot/grid clipping state exposed by Datoviz is inspectable from the
  snapshot.
- Snapshots are immutable after return.
- Resizes and view/layout changes produce changed ids or revisions.
- Existing grid clipping remains correct and is not regressed by the snapshot work.

## Stop Conditions

- Stop if render uses layout state that is absent from the snapshot.
- Stop if snapshot ids are mutable or unstable.
- Stop if logical pixels and framebuffer pixels cannot be distinguished in the API.
- Stop before changing GSP capability claims.
