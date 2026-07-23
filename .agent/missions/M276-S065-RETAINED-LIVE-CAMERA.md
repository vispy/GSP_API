# M276 - S065 retained and live camera behavior

## Status

Completed in GSP commit `42ac325` and VisPy2 commit `0dce6d6`. The amended non-native slice passed
independent supervisor review. Native qualification remains deferred to M284, and live Datoviz
capability promotion remains forbidden until that checkpoint.

## Goal

Make programmatic and interactive View3D camera changes reliable, retained, capability-declared,
and ready for human review.

## Amended work

- Fix renderer shutdown so `live_view3d_navigation` is unsubscribed before native objects are
  destroyed; prove exact callback cleanup and idempotent close with synthetic bindings.
- Add Datoviz session plumbing for View3D only when the session capability snapshot already
  advertises `view3d.navigation.orbit_pan_zoom.v1`. Static/offscreen rendering remains
  noninteractive and the current experimental/native gate remains closed.
- Prove programmatic orbit/pan/zoom/reset update canonical retained state while unchanged visual
  buffers are not re-uploaded.
- Add deterministic Matplotlib re-render/update coverage from revised View3D state.
- Add a VisPy2 camera example with explicit caller-owned session lifecycle and clear wording that
  live Datoviz input is deferred pending M284 qualification.
- Run at least 25 synthetic create/enable/update/close cycles for callback and retained-state
  regression evidence. Do not describe these as native qualification.

## Locks

- `gsp`: backend sessions, navigation bindings/capabilities/tests
- `vispy2`: camera display example and focused tests

## Acceptance

Programmatic camera changes pass both backends. Synthetic Datoviz lifecycle tests prove exact
callback cleanup, idempotent close, and no camera-only visual re-upload. Full tests, strict typing,
lint, wheels, and the example pass. Live Datoviz navigation remains unadvertised, and no native
lifecycle claim is made.

## Deferred human checkpoint

M284 must run genuine timeout-bounded native lifecycle iterations in a GUI-capable environment and
owner interaction review before live Datoviz capability promotion. M277 may proceed after this
amended non-native slice passes supervisor review.

## Stop conditions

Stop on callback leak, full visual re-upload for camera-only changes, hidden thread/event-loop
ownership, a need to edit Datoviz, or any attempt to promote live Datoviz capability without M284
native evidence. Do not execute native Datoviz app/window probes in this amended slice.
