# M187 - S043 Datoviz retained DATA-space View3D visuals

## Stage

S043 - Datoviz Panel Frame, Guide Strictness, And Retained View3D

## Status

Draft.

## Summary

Implement Datoviz retained DATA-space `View3D` visual attachments and retained update instrumentation
needed for strict live orbit/pan/zoom.

## Deliverables

- Explicit DATA_3D mesh visual attachment path.
- Camera/projection uniform update path that does not rewrite unchanged mesh vertex/index buffers.
- Retained update stats for vertex uploads, index uploads, visual rebuilds, view/projection uniform
  updates, and snapshot resolves.
- Snapshot camera/projection readback.
- Ray query from the same frame snapshot used by render.
- Native Datoviz tests for static DATA-space rendering, orbit/pan/zoom update counters, visual
  identity stability, snapshot changes, ray query snapshot equality, resize, and multi-panel
  isolation.

## Acceptance

- Camera/projection changes alter screen projection without vertex/index buffer writes.
- Mesh visual identity remains stable across navigation.
- Ray/query state matches render state by snapshot id.

## Stop Conditions

- Stop if ordinary camera updates require CPU vertex reprojection.
- Stop if unchanged visual buffers are reuploaded during ordinary navigation.
- Stop if visual identity changes during navigation.
- Stop if query/ray state diverges from render state.
