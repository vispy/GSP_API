# M183 - S043 Datoviz unified view descriptors

## Stage

S043 - Datoviz Panel Frame, Guide Strictness, And Retained View3D

## Status

Ready.

## Summary

Replace public mutable Datoviz panel-view structs with revisioned `DvzView2D` and `DvzView3D`
descriptors and state readback APIs.

## Deliverables

- `DvzView`, `DvzView2DDesc`, and `DvzView3DDesc` API design and implementation.
- Ordered `View2D` domain support, including reversed domains.
- Revisioned camera/projection state for `View3D`.
- Canonical view state readback.
- Temporary `dvz_panel_set_domain()` compatibility wrapper over the active `DvzView2D`.
- Native tests for domain ordering, reversal, view revision changes, camera/projection readback, and
  native controller synchronization boundaries.

## Acceptance

- View2D domain ordering and reversal are explicit and test-backed.
- View3D camera/projection can be read back canonically.
- View revisions are reflected in `DvzPanelFrameSnapshot`.
- Native controller state cannot mutate private matrices without synchronized readable state.

## Stop Conditions

- Stop if View2D reversed domains cannot be represented.
- Stop if View3D camera/projection readback cannot match the rendered state.
- Stop if native controllers mutate state that cannot be expressed as canonical camera/projection
  state.
