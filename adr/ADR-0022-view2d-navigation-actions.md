# ADR-0022 - View2D Navigation Actions

## Status

Accepted

## Context

GSP has an accepted 2D transform/view baseline: `View2D` is deterministic panel-level state with
finite linear x/y limits, and pan/zoom are represented as explicit `View2D` updates. The project now
needs live interaction without freezing a broad GUI event model or leaking backend-native controllers.

The performance target is GPU-retained interaction. For Datoviz and similar backends, changing the
view during pan/zoom should update small panel view/projection or data-to-clip state, typically
uniform buffers, while visual geometry, image, texture, and index buffers remain resident.

## Decision

S035 accepts a narrow `View2D` navigation action model:

- Public navigation input is semantic action data: `pan_by`, `zoom_about`, `set_view`, and
  `reset_view`.
- Public navigation output is an explicit updated `View2D` plus old/new revision identifiers,
  snapshot identifiers where available, acceptance status, and diagnostics.
- Native mouse, wheel, keyboard, touch, toolkit, browser, Datoviz, Matplotlib, or VisPy events are
  backend or producer adapters into these semantic actions. They are not public protocol semantics.
- A `View2DNavigationController` targets one panel/view pair and owns no hidden rendering transform.
  Its normative effect is only to produce a new accepted `View2D` state.
- Navigation actions use resolved panel logical-pixel coordinates and the matching
  `layout_snapshot_id` when layout information is required.
- Render, query, and readback results must identify the same `View2D` revision or view snapshot used
  to produce them whenever navigation strictness is claimed.
- Retained GPU backends must implement the strict fast path by updating panel/view/projection or
  equivalent uniform/state data for unchanged visuals. Re-uploading unchanged visual buffers during
  pan/zoom is an adapted fallback, not the strict high-performance path.

## Boundary with backend-native interaction systems

Backend-native interaction implementations may exist independently of GSP. Datoviz, Matplotlib,
VisPy, and future backends may expose their own native pan/zoom, camera, picking, selection,
brushing, or gesture systems for direct backend users and backend-native demos.

Those native implementations are not the source of truth for strict GSP semantics. Strict GSP
navigation uses backend input only as an event source: backend adapters normalize event type,
coordinates, buttons, modifiers, wheel deltas, device scale, and coordinate-origin conventions,
then submit semantic events or actions to the GSP navigation controller. The accepted GSP `View2D`
state remains canonical.

This means some interaction behavior may intentionally exist in both a backend project and GSP.
That duplication is acceptable across project boundaries when the two systems serve different API
contracts: backend-native interaction serves native backend users, while GSP interaction serves
backend-neutral protocol consistency. It is not acceptable for strict GSP behavior to depend on
hidden backend-native state unless that state is synchronized back into canonical GSP state and
covered by conformance tests.

## Consequences

Workers can add useful live pan/zoom while preserving deterministic replay. A recorded action
sequence and initial `View2D` can be replayed without the original backend event stream.

Backends may expose live input conveniences, but capability records must distinguish semantic
navigation support, live native input adaptation, retained GPU update placement, CPU remap fallback,
and unsupported behavior.

Public 3D camera/projection, orbit/trackball controllers, linked views, selection, hover, brushing,
gesture recognition, event propagation, focus management, and user callback dispatch remain deferred.
