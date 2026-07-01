# S042 Scoping - Live Interactive Review Examples

## Stage Goal

Make the review examples behave like interactive review tools in live mode, across 2D and 3D where
backend support exists, while preserving canonical GSP navigation semantics.

## Current State

| Area | State | Notes |
|---|---|---|
| Matplotlib View2D | Implemented | `examples/review/_review_runner.py` adapts mouse drag/wheel to S035 `View2DNavigationAction` when `--interactive-navigation` is passed. |
| Matplotlib View3D | Implemented | `examples/review/_review_runner.py` adapts drag/wheel/key input to S037 `View3DNavigationAction` when `--interactive-navigation` is passed. |
| Datoviz View2D | Implemented but needs review-pack validation | `DatovizV04ProtocolRenderer.enable_gsp_view2d_navigation()` subscribes to Datoviz pointer input and applies retained S035 updates. |
| Datoviz View3D | Static only | Datoviz renders public `View3D` state, but live orbit/pan/zoom is not implemented. |

## Authority And Boundary

Follow the existing authority chain:

1. `PROJECT_CHARTER.md`
2. `ARCHITECTURE.md`
3. `SPEC_INDEX.md`
4. `spec/navigation.md`
5. `spec/view3d_navigation.md`
6. accepted ADRs and `.agent/decisions/`
7. existing source code

The key boundary is already accepted: raw mouse, wheel, keyboard, toolkit, Matplotlib, or Datoviz
events are not public protocol. Backend events must be adapted into canonical GSP navigation actions,
then applied to canonical `View2D` or `View3D` state. Backend-native camera/controller objects remain
private implementation details.

## Scope

In scope:

- Make live review examples try GSP navigation by default where supported.
- Keep offscreen rendering static and deterministic.
- Add a way to force static live windows, for example `--no-interactive-navigation`.
- Keep `--interactive-navigation` as a compatibility alias if useful.
- Validate Matplotlib 2D drag pan and wheel zoom across review examples with `View2D`.
- Validate Matplotlib 3D orbit/pan/zoom/reset across review examples with `View3D`.
- Validate Datoviz 2D live navigation across review examples with `View2D`.
- Implement Datoviz 3D live navigation only through canonical S037 actions and retained camera/view
  updates.
- Add tests or smoke coverage proving navigation does not rebuild or reupload unchanged visual
  buffers in retained Datoviz paths.
- Update documentation and capability tables after support is proven.

Out of scope:

- Public raw event streams.
- Public backend-native Matplotlib or Datoviz camera/controller APIs.
- Datoviz native arcball as public GSP semantics.
- Perspective navigation unless a separate ADR/spec accepts it.
- Gesture, kinetic scrolling, touch, linked views, and visual picking.
- Full migration of every legacy script under `examples/`; this stage targets the protocol review
  examples first.

## Proposed Mission Stack

| Mission | State | Purpose |
|---|---|---|
| M180 | ready | Make protocol review examples interactive in live mode and implement/prove Datoviz View3D navigation if the v0.4 bindings support retained updates. |

If M180 becomes too large, split it:

| Mission | Purpose |
|---|---|
| M180A | Review runner defaults and Matplotlib/Datoviz View2D validation. |
| M180B | Datoviz View3D binding evidence and retained navigation implementation. |
| M180C | Capability/docs/tests closeout. |

## Implementation Plan

1. Preserve existing changes and inspect worktree safety with `git status --short --branch`.
2. Update `examples/review/_review_runner.py` live-mode behavior:
   - live mode enables navigation by default for supported scenes;
   - `--no-interactive-navigation` forces static live windows;
   - `--interactive-navigation` remains accepted for compatibility or becomes a no-op alias;
   - offscreen mode rejects or ignores navigation as today.
3. Verify Matplotlib review behavior:
   - `View2D`: left-drag pan, wheel zoom;
   - `View3D`: left-drag orbit, right/middle-drag pan, wheel zoom, `r` reset;
   - re-render uses updated canonical `View2D`/`View3D` state.
4. Validate Datoviz View2D review behavior:
   - live `scene.view` examples call `enable_gsp_view2d_navigation(scene.view)`;
   - unavailable input bindings produce a static-window warning, not a crash;
   - retained update tests prove visual buffers are not recreated or reuploaded.
5. Implement Datoviz View3D live navigation:
   - add `DatovizV04ProtocolRenderer.enable_gsp_view3d_navigation()`;
   - subscribe to Datoviz pointer input on the live view;
   - map left drag to `ORBIT`, right/middle drag to `PAN`, wheel to `ZOOM`;
   - apply actions through `apply_view3d_navigation_action()`;
   - update the live Datoviz camera/projection from the resulting canonical `View3D`;
   - maintain revision and projection snapshot consistency for query/ray readback;
   - do not rebuild visual objects or reupload unchanged visual buffers.
6. Add focused verification:
   - fake-facade tests for Datoviz View3D navigation action flow;
   - review-runner tests for live navigation default and static fallback;
   - smoke command for Matplotlib and Datoviz review paths;
   - documentation examples for side-by-side review commands.
7. Update capability documentation only after tests prove the path:
   - `view3d.navigation.orbit_pan_zoom.v1` for Datoviz remains unclaimed until retained live
     navigation is implemented and verified;
   - Datoviz native arcball remains private/native-only unless canonical synchronization is proven.

## Suggested Commands

Matplotlib 2D:

```bash
PYTHONPATH=src .venv/bin/python examples/review/01_scatter_basic.py --backend matplotlib --live
```

Matplotlib 3D:

```bash
PYTHONPATH=src .venv/bin/python examples/review/10_view3d_flat_lambert.py --backend matplotlib --live
```

Datoviz 2D:

```bash
PYTHONPATH=src .venv/bin/python examples/review/01_scatter_basic.py --backend datoviz --live
```

Datoviz 3D target:

```bash
PYTHONPATH=src .venv/bin/python examples/review/10_view3d_flat_lambert.py --backend datoviz --live
```

Review pack:

```bash
tools/compare-review-examples --live-side-by-side --interactive-navigation examples/review/10_view3d_flat_lambert.py
```

## Acceptance

- Live Matplotlib review examples with `View2D` are mouse interactive by default.
- Live Matplotlib review examples with `View3D` are mouse interactive by default.
- Live Datoviz review examples with `View2D` are mouse interactive when local v0.4 input bindings are
  available.
- Live Datoviz review examples with `View3D` support canonical orbit/pan/zoom if, and only if, the
  retained camera/projection update path is implemented and tested.
- Offscreen output remains deterministic and non-interactive.
- Static fallback diagnostics are clear when a backend lacks required live input or retained update
  bindings.
- Capability docs match proven behavior.

## Stop Conditions

- Stop if implementing Datoviz View3D requires exposing native Datoviz arcball/controller objects as
  public GSP API.
- Stop if the v0.4 binding layer cannot update live View3D camera/projection state without rebuilding
  the scene; record an evidence note instead.
- Stop if the work requires changing accepted S035/S037 navigation semantics; create a ChatGPT Pro
  consultation packet before changing protocol behavior.
- Stop if tests reveal existing spec/source conflicts rather than inventing a third behavior.

## Open Risks

- Datoviz v0.4 live View3D camera/projection setters may be incomplete or unstable.
- Datoviz pointer and key input coverage may not support reset without additional bindings.
- Existing capability tables may contain stale wording for Datoviz View2D native drag/wheel review.
- Legacy non-review examples use older APIs and should not be folded into this stage without a
  separate migration pass.
