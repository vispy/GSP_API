# M188 - S043 GSP Datoviz View3D live navigation

## Stage

S043 - Datoviz Panel Frame, Guide Strictness, And Retained View3D

## Status

Draft.

## Summary

Enable Datoviz `View3D` live navigation in GSP review paths behind retained DATA-space capability
gates.

## Deliverables

- Datoviz capability gate for retained DATA-space visuals and retained update stats.
- GSP canonical `View3D` action replay into Datoviz camera/projection state.
- Datoviz state readback equality checks against canonical GSP state.
- Retained update counter assertions proving unchanged visual buffers are not reuploaded.
- Ray readback after initial/orbit/pan/zoom/reset navigation steps.
- Review artifacts for Datoviz live `View3D` initial/orbit/pan/zoom/reset.
- Documentation and capability table updates.

## Acceptance

- `view3d.navigation.orbit_pan_zoom.v1` is advertised only when retained navigation is proven.
- Live Datoviz `View3D` review examples enable navigation only behind capability gates.
- Static fallback diagnostics remain clear for older Datoviz builds.

## Stop Conditions

- Stop if Datoviz controller effects cannot be synchronized to canonical GSP state.
- Stop if unchanged visual buffers are reuploaded during ordinary navigation.
- Stop if GSP would have to expose Datoviz controller names publicly.
