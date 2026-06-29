# S035 View2D Navigation Contract Decisions

Status: accepted by M147 from P019 response and user performance guidance.

## Accepted

- S035 adds deterministic `View2D` navigation actions rather than a broad public event model.
- Accepted actions are `pan_by`, `zoom_about`, `set_view`, and `reset_view`.
- Each accepted action produces an explicit updated `View2D` and a new view revision/snapshot.
- Native mouse, wheel, keyboard, touch, Datoviz, Matplotlib, VisPy, browser, or toolkit events are
  backend/producer adapters into semantic actions. They are not public protocol semantics.
- Render, query, readback, guides, and layout-strict results must refer to matching view/layout
  snapshots when strictness is claimed.
- Retained GPU backends must implement the strict fast path through small panel view/projection or
  data-to-clip uniform/state updates when visual data are unchanged.

## Capability-Gated

- Live native input adaptation is separate from programmatic navigation action support.
- Datoviz retained navigation support must be proven by showing pan/zoom updates panel/view state
  without `dvz_visual_set_data` or equivalent visual-buffer uploads for unchanged data.
- CPU remap fallback is allowed only as an explicit adapted placement.

## Deferred

Raw event streams, callback dispatch, hover/selection/brushing, linked views, gesture recognition,
event propagation, focus management, backend-native controllers, public `View3D`, public camera and
projection semantics, orbit/trackball controllers, and 3D picking.

## Source

`.agent/consultations/P019-response.md` converted into ADR-0022 and `spec/navigation.md`.
