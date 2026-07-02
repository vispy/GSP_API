# P029 - Datoviz View3D Live Navigation Failure and Long-Term Contract

## Purpose

This needs ChatGPT Pro consultation.

Manual review shows that Datoviz View3D live interaction in `examples/review/12_view3d_mesh_pick.py`
still has no visible effect, despite retained View3D camera update fixes and passing synthetic input
tests. Dependent implementation should pause until the consultation result is pasted or committed.

## Prompt

You are reviewing an architecture/API decision for `GSP_API`, a Python visualization protocol/library
with Matplotlib and Datoviz v0.4-dev backends plus a VisPy2-style producer API.

The specific issue is Datoviz live View3D navigation. The user manually tested the Datoviz backend
review example and reports that interaction still does not work. We need a long-term decision, not
another speculative local patch.

Answer as a protocol/API architect. Do not generate implementation code unless it clarifies a test
or contract. The expected output format is at the end.

### Project Authority and Constraints

Authority order in this repo is:

1. `PROJECT_CHARTER.md`
2. `ARCHITECTURE.md`
3. `SPEC_INDEX.md`
4. `spec/**`
5. accepted ADRs in `adr/**` and `.agent/decisions/**`
6. `LEGACY_MAP.md`
7. existing source code

Existing code is implementation material, not automatically authoritative. If legacy code conflicts
with accepted specs, specs win.

The public protocol is backend-neutral. It must not expose backend-native Datoviz shader names,
Vulkan draw-state, framebuffer attachment names, controller objects, Matplotlib artists/axes, raw
GLFW events, Datoviz object ids, or pipeline internals as public API.

Local repositories:

- GSP_API: `/home/cyrille/GIT/Viz/GSP_API`
- Datoviz: `/home/cyrille/GIT/Viz/datoviz`

Do not assume Datoviz v0.4-dev API compatibility is sacred. The user allows breaking Datoviz
v0.4-dev API compatibility for better long-term architecture, but GSP public API must stay
backend-independent.

### Accepted Current GSP State

GSP has a bounded public 3D baseline:

- `Camera3D(eye, target, up)`.
- `OrthographicProjection3D(xlim, ylim, near_far)`.
- `View3D(id, panel_id, camera, projection, depth_mode=opaque_less, revision=...)`.
- Orthographic projection only.
- `MeshVisual.positions` accepts `(N, 2)` and `(N, 3)`.
- `(N, 3)` plus `CoordinateSpace.DATA` projects through `View3D`.
- `(N, 3)` plus `CoordinateSpace.NDC` is interpreted as panel NDC3 directly.
- Existing 2D affine transforms do not apply to `(N, 3)` mesh geometry.
- `View3DProjectionSnapshot` provides deterministic projection snapshot ids.
- `View3DNavigationAction` provides canonical orbit, pan, zoom, set, and reset actions.

The accepted navigation protocol requires:

- navigation actions are canonical GSP actions;
- stale layout/view/projection snapshots are rejected;
- accepted actions increment the public `View3D.revision`;
- renderers may use native camera/input internally only if the resulting state synchronizes back into
  canonical `View3D` and passes revision/snapshot tests.

### Datoviz Implementation State Before Manual Failure

Datoviz v0.4-dev is intended as the high-performance GPU backend.

Current Datoviz retained View3D rendering:

- DATA-space meshes attach to a Datoviz panel-owned View3D path instead of CPU-projected panel NDC.
- The adapter uses retained mesh buffers and should update camera/projection without reuploading
  unchanged vertex/index buffers.
- The latest local fix changed retained camera updates to prefer
  `dvz_panel_view3d_desc()` plus `dvz_panel_set_view3d_desc()`, falling back to
  `dvz_panel_set_camera()`. It no longer mutates only a borrowed camera with `dvz_camera_set_view()`.

Current Datoviz live navigation adapter:

- `enable_gsp_view3d_navigation()` subscribes to `dvz_view_input(live_view)`.
- `_DatovizLiveView3DNavigation` converts Datoviz pointer events to canonical GSP actions:
  left-drag orbit, right-drag pan, wheel zoom, double-click reset.
- Accepted actions are replayed through `apply_gsp_view3d_navigation_action()`.
- The renderer requests a new Datoviz frame after accepted actions.

Evidence that passed before the manual failure:

- Synthetic fake-Datoviz tests prove canonical actions update `View3D` and do not reupload mesh
  buffers.
- Imported Datoviz tests using `dvz_input_router()` and `dvz_input_emit_event()` prove that directly
  emitted union pointer events can reach the Python callback and drive the reducer.
- Offscreen review comparison renders example 12 for Matplotlib and Datoviz.
- Live Datoviz example prints an enabled message when navigation is available.

Evidence that now invalidates the support claim:

- Manual live testing of `examples/review/12_view3d_mesh_pick.py --backend datoviz --frames 1`
  still shows no working interaction.
- Therefore the synthetic tests prove only the reducer and emitted-event path, not real GLFW window
  event production, panel coordinate routing, controller binding, render invalidation, or native
  Datoviz camera state synchronization.

### Local Datoviz API Findings

Local Datoviz binding observations:

- The Python binding keeps C callbacks alive for `dvz_input_subscribe_event()` through an internal
  callback keepalive store, so callback garbage collection is probably not the root cause.
- Datoviz live windows create a `DvzPointerGestureHandler` in the window host, so gesture-derived
  `DRAG` events should exist in the native input stack.
- Datoviz exposes `dvz_panel_connect_input(panel, router)`.
- Datoviz exposes native controller paths including `dvz_arcball()`, `dvz_turntable()`,
  `dvz_view_arcball()`, and `dvz_view_bind_controller()`.
- Existing legacy manual examples in this repo have used native Datoviz `panel.arcball(...)`; those
  examples are legacy/evidence-only until canonical synchronization is accepted.

### Existing Architecture Notes

An earlier closeout said Datoviz View3D live navigation must remain deferred until either native
DATA-space mesh rendering or a retained strategy was proven. A later mission promoted it after
synthetic proofs. The manual failure reopens that promotion.

A Datoviz panel-frame architecture note identifies a longer-term target: Datoviz should provide a
bounded panel frame snapshot/revision model, with proofs before retained View3D navigation is
advertised:

- DATA-space mesh path is native and retained.
- Camera/projection updates do not reupload unchanged mesh buffers.
- View/projection snapshot id changes after accepted navigation.
- Ray/query uses the render snapshot being shown.
- Multi-panel routing and isolation are explicit.

### Candidate Long-Term Paths

Consider these options, or propose a better one:

1. Keep the custom GSP reducer and direct `dvz_view_input()` subscription, but require stronger live
   window tests and possibly `dvz_panel_connect_input(panel, router)` for panel-coordinate routing.
2. Use Datoviz native arcball/turntable controllers for real interaction, but require public readback
   or synchronization back into canonical `View3D` revisions and snapshots.
3. Require Datoviz API changes before support is claimed: a panel-frame snapshot contract, native
   controller state readback, canonical camera/projection revision evidence, and explicit input
   routing semantics.
4. Defer Datoviz View3D live navigation entirely and keep only static retained View3D rendering plus
   ray-context query support until the panel-frame/controller contract exists.

The current short-term mitigation is to stop advertising `view3d.navigation.orbit_pan_zoom.v1` by
default for Datoviz. The experimental custom reducer can remain opt-in via
`GSP_DATOVIZ_ENABLE_EXPERIMENTAL_VIEW3D_NAV=1` for diagnostics, but examples should not claim support
by default.

### Questions To Answer

1. What is the recommended long-term path for Datoviz View3D live navigation?
2. Is a custom GSP reducer over Datoviz pointer events a good long-term design, or should Datoviz
   native controllers be the source of truth with canonical synchronization?
3. What exact Datoviz v0.4 API changes, if any, should be requested before GSP advertises support?
4. What public GSP invariants must be proven before `view3d.navigation.orbit_pan_zoom.v1` is
   advertised for Datoviz?
5. What tests are required to distinguish synthetic reducer success from real live window success?
6. Should the recent retained-camera update fix be kept, reverted, or narrowed while navigation is
   de-advertised?
7. What should example 12 do in the meantime: static Datoviz live window, opt-in experimental
   navigation, native Datoviz-only controller demo clearly marked noncanonical, or something else?

### Expected Output Format

Please answer in this exact structure:

```text
Recommendation:
- [One of: defer, custom reducer, native controller sync, Datoviz API change first, other]
- Rationale:

Short-Term Policy:
- Capability advertisement:
- Example 12 behavior:
- Whether to keep the experimental env opt-in:

Required Datoviz Contract:
- Required APIs:
- Required revision/snapshot semantics:
- Required input routing semantics:

Required GSP Invariants:
- View3D state:
- Layout/view/projection freshness:
- Buffer upload behavior:
- Query/picking consistency:

Test Plan:
- Unit tests:
- Imported Datoviz binding tests:
- Real live/manual or automated window tests:
- Stop conditions:

Disposition of Current Patch:
- Keep/revert/narrow the retained-camera update:
- Keep/revert/narrow the custom reducer:
- Next implementation step:
```
