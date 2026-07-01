# M180 - S042 live interactive review examples

## Stage

S042 - Live Interactive Review Examples

## Status

Completed by local-main-codex.

## Summary

Make protocol review examples interactive in live mode across Matplotlib and Datoviz where backend
support exists. Preserve canonical GSP navigation semantics: backend mouse/wheel/key events are
private inputs that lower to S035/S037 navigation actions and produce updated canonical `View2D` or
`View3D` state.

## Deliverables

- Live review runner defaults to interactive navigation for supported `View2D` and `View3D` scenes.
- Static live fallback flag and clear diagnostics for unavailable backend input bindings.
- Matplotlib 2D and 3D review examples validated under live interactive navigation.
- Datoviz 2D review examples validated under live retained navigation.
- Datoviz 3D `enable_gsp_view3d_navigation()` implemented as an evidence-backed unsupported
  diagnostic because v0.4 retained camera/projection updates cannot move the current CPU-projected
  fixed mesh uploads.
- Fake-facade or smoke tests proving retained Datoviz navigation does not rebuild/reupload unchanged
  visual data.
- Updated review README and capability documentation.

## Acceptance

- `examples/review/*` live Matplotlib `View2D` examples support drag pan and wheel zoom without
  passing a hidden opt-in flag.
- `examples/review/*` live Matplotlib `View3D` examples support left-drag orbit, right/middle-drag
  pan, wheel zoom, and `r` reset without passing a hidden opt-in flag.
- Datoviz `View2D` review examples support drag pan and wheel zoom when live input bindings are
  available, and degrade to a static live window with a warning otherwise.
- Datoviz `View3D` review examples either support canonical orbit/pan/zoom through retained
  camera/projection updates, or emit a documented evidence-backed unsupported diagnostic.
- Offscreen rendering remains non-interactive and deterministic.
- Capability docs only advertise Datoviz `view3d.navigation.orbit_pan_zoom.v1` if the retained
  implementation is tested.

## Stop Condition

Stop before changing public navigation protocol semantics. Stop before exposing Datoviz native
arcball/controller objects as public API. If Datoviz v0.4 bindings are insufficient for retained
View3D updates, write an evidence note and leave Datoviz 3D live navigation unsupported.

## Handoff

Follow-up work should start with `.agent/S042_SCOPING.md`. Relevant implementation anchors:

- `examples/review/_review_runner.py`
- `examples/review/README.md`
- `tools/compare-review-examples`
- `src/gsp_datoviz/protocol_renderer.py`
- `src/gsp_matplotlib/navigation.py`
- `spec/navigation.md`
- `spec/view3d_navigation.md`
- `spec/backend_capabilities_visuals.md`
- `.agent/decisions/S035_view2d_navigation_contracts.md`
- `.agent/decisions/S037_view3d_navigation_datoviz_contracts.md`

## Result

Completed. Live review now defaults to GSP navigation where supported, with
`--no-interactive-navigation` as the static live opt-out. Datoviz `View3D` navigation is explicitly
unsupported with an evidence-backed diagnostic: the current renderer uploads CPU-projected
panel-NDC mesh positions with fixed controller mode, so native camera updates alone cannot move the
mesh and per-event visual buffer reupload would violate the retained-navigation boundary.
