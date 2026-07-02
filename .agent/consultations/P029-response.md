# P029 Response - Datoviz View3D Live Navigation Decision

Status: direct in-agent decision after local Datoviz source inspection.

## Recommendation

Use Datoviz panel-bound native controller/input routing as the long-term route, not the direct Python
`dvz_input_subscribe_event()` custom reducer.

The supported Datoviz path is:

1. create/bind a scene-owned native controller to the panel;
2. connect the panel to the live view input router with `dvz_panel_connect_input()` or
   `dvz_view_bind_controller()`;
3. let Datoviz route window input through panel-local coordinate conversion and controller dispatch;
4. read back canonical panel `View3D` state with `dvz_panel_view3d_state()`;
5. synchronize that state into GSP `View3D`, including revision/snapshot ids.

The current direct Python reducer should remain diagnostic-only. It can prove action replay and
buffer non-reupload behavior, but it bypasses Datoviz's native panel input path, panel-local
coordinate conversion, controller dispatch, and panel View3D revision machinery.

## Evidence From Datoviz Source

- `dvz_view_bind_controller()` binds a controller to a panel and calls `dvz_panel_connect_input()`.
- `dvz_panel_connect_input()` subscribes `_scene_panel_input_callback()` to the router.
- `_scene_panel_input_callback()` converts window pointer events to figure coordinates, dispatches
  through bound panel controllers, and resizes panel cameras on resize.
- Native controller dispatch checks panel targeting, applies panel-local coordinates, and handles
  drag capture.
- Turntable/fly controllers mutate the panel camera and call `_scene_panel_view3d_dirty()`, which
  increments `panel->view3d_revision` and requests a frame.
- `dvz_panel_view3d_state()` exposes enabled state, view id, revision, camera view/projection,
  explicit orthographic bounds, and matrices.
- Datoviz tests already cover panel input routing, HiDPI figure-coordinate conversion, panel
  View3D state readback, and panel-frame info carrying the View3D revision.

## Controller Choice

For GSP `Camera3D` synchronization, prefer Datoviz turntable over arcball.

Arcball is useful for Datoviz-native model interaction, but the source shows it is primarily a
model/MVP transform path. It does not naturally map to GSP's canonical `Camera3D(eye, target, up)`
state.

Turntable is closer to GSP orbit/pan semantics because it owns eye, pivot/target, up, yaw/pitch, and
distance, and applies those values to a `DvzCameraView`.

## Projection Zoom Gap

Turntable cannot be advertised as full `view3d.navigation.orbit_pan_zoom.v1` without one more
contract decision.

GSP's `Zoom3DPayload` scales orthographic projection bounds. Datoviz turntable's wheel path calls
`dvz_turntable_dolly()`, which changes camera distance. For an orthographic camera, camera-distance
dolly is not the same public semantic as scaling `OrthographicProjection3D.xlim`/`ylim`.

Therefore, the long-term fix needs either:

- a Datoviz native orthographic zoom controller/API that changes explicit orthographic bounds; or
- a GSP adapter that lets native Datoviz turntable own orbit/pan, while GSP handles wheel zoom by
  updating `dvz_camera_set_orthographic_bounds()` and then synchronizes through
  `dvz_panel_view3d_state()`.

The second option is acceptable as an intermediate implementation if it still uses
`dvz_panel_connect_input()` for panel routing and does not advertise support until real live window
proofs pass.

## Short-Term Policy

Keep `view3d.navigation.orbit_pan_zoom.v1` hidden for Datoviz by default.

Keep `GSP_DATOVIZ_ENABLE_EXPERIMENTAL_VIEW3D_NAV=1` as a diagnostic opt-in for the old reducer, but
do not treat that path as the supported architecture.

Example 12 should continue opening a static Datoviz live window by default. If a native Datoviz-only
interaction demo is useful, it must be explicitly labeled noncanonical until GSP synchronization is
implemented and proven.

## Required Proofs Before Re-Advertising

- Real live window input uses Datoviz panel routing, not only synthetic `dvz_input_emit_event()`.
- Orbit and pan update Datoviz panel camera state and synchronize into canonical GSP `View3D`.
- Orthographic zoom has GSP projection-bound semantics, not only camera-distance dolly.
- Accepted navigation changes GSP `View3D.revision` and the Datoviz panel View3D revision/snapshot.
- Retained DATA-space mesh buffers are not reuploaded during navigation.
- Ray/pick queries use the same layout/view/projection snapshot as the rendered frame.
- Multi-panel input targets only the intended panel.

## Disposition Of Current Patch

Keep the retained-camera update fix. It is still a correct lower-level repair for applying canonical
GSP View3D state to Datoviz panel camera/projection state.

Keep the experimental reducer only as a diagnostic harness. Do not build the long-term supported
feature on it.

Next implementation step: add a native Datoviz View3D navigation experiment that binds a turntable
to the panel, connects panel input through the live view router, reads back `dvz_panel_view3d_state()`,
and handles/proves orthographic projection zoom before capability promotion.
