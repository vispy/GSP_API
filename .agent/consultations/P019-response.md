## 1. Recommendation summary

* **Release the current approved 2D/static API as v0.1 before adding interactivity.** Do not make pan/zoom, event semantics, or 3D a release blocker. The six reviewed examples already define a coherent public baseline.

* **Next feature stage should be narrow public `View2D` pan/zoom navigation, not a general event system.** Define protocol-owned navigation actions that deterministically produce explicit `View2D` updates. Backend mouse/wheel events are adapters, not public semantics.

* **Keep render/query/readback coherence as the central invariant.** Every accepted navigation update must produce a new `View2D` revision/snapshot, and render/query results must report the matching view/layout snapshot ids.

* **Add public `View3D` soon, but after `View2D` navigation.** Start with static camera/projection/depth semantics sufficient to make `(N,3)` MeshVisual protocol data useful. Defer orbit controllers, arbitrary 3D picking, lighting, materials, and advanced clipping.

* **Allow Datoviz-native live behavior experimentally only when it lowers to protocol-owned state.** Native interactivity may be used internally, but the public contract is still `View2D`/`View3D` state plus structured capability diagnostics.

* **Do not import Matplotlib, Datoviz, VisPy, browser, Qt, or DOM event models.** The protocol should define a small semantic navigation layer and let backends adapt into it.

---

## 2. Stage plan

| Stage                                                      | Goal                                                                                                                            | Public semantics added                                                                                                                                                                                                                                      | Backends                                                                                                                                                                                                                                                            | Fixtures                                                                                                                                                                                                                                                                                                                                    | Stop condition                                                                                                                                                                                                      |
| ---------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **S034 — v0.1 Static 2D Release Lock**                     | Ship the current reviewed API as the first stable baseline. Preserve the approved examples and avoid widening the release gate. | No new feature semantics. Freeze current 2D scene, visual, guide, layout, render/query/readback semantics as v0.1.                                                                                                                                          | Matplotlib reference behavior remains strict. Datoviz v0.4 mapping remains adapted but documented. VisPy2-style producer layer remains producer-side only.                                                                                                          | Release fixtures for the six reviewed examples: scatter, image, points-over-image, guides/ticks, color mapping + colorbar, text labels. Include render/query/readback snapshot checks where layout strictness is claimed.                                                                                                                   | v0.1 is tagged/released with capability matrix and known unsupported diagnostics. No interactivity or 3D promises are added to v0.1.                                                                                |
| **S035 — `View2D` Navigation Controller v1**               | Add useful live 2D pan/zoom without defining a full public event/callback system.                                               | Optional capability: `interaction.view2d.navigation.v1`. Add protocol-owned navigation actions: `pan_by`, `zoom_about`, `set_view`, `reset_view`. Each accepted action produces an explicit `View2D` update and new view revision/snapshot.                 | Matplotlib may support programmatic navigation fixtures first, with live GUI input optional/unsupported. Datoviz may adapt native mouse/wheel interaction into protocol actions. VisPy2 producer conveniences may lower to these actions.                           | Numeric fixtures for action sequences: initial `View2D` + panel viewport + pan/zoom actions → expected `View2D`. Render/query fixtures must verify matching `view_snapshot_id` and `layout_snapshot_id`. Negative fixtures for stale snapshots, non-finite values, non-invertible transforms, unsupported live input.                       | At least one strict backend path passes deterministic programmatic pan/zoom fixtures. All backends report accurate capability support/unsupported diagnostics. No backend-native event model leaks into public API. |
| **S036 — Minimal `View3D` / Camera / Projection Baseline** | Make protocol-owned 3D real enough for `(N,3)` MeshVisual data, while avoiding a full 3D engine object model.                   | Optional capability: `view3d.camera.v1`. Add `View3D` with finite camera pose, projection parameters, viewport binding, near/far clipping, and deterministic world→clip→panel projection. Add depth semantics only as needed for basic 3D points/triangles. | Datoviz is likely the first meaningful rendering target. Matplotlib may be partial or unsupported for strict 3D rendering, but can still participate in projection/readback diagnostics if implemented. VisPy2 producer may emit `View3D` state, not own semantics. | Matrix/projection fixtures: camera pose → expected projected coordinates. Basic depth-order fixtures for simple triangles/points. Capability-gated `(N,3)` MeshVisual fixtures. Query/readback fixtures must report matching `view3d_snapshot_id`, layout snapshot, projection mode, and unsupported 3D query diagnostics where applicable. | `(N,3)` MeshVisual is accepted only when paired with an accepted `View3D` capability. Static 3D render/projection behavior is deterministic. Orbit, lighting, materials, and arbitrary 3D picking remain deferred.  |

---

## 3. Minimal accepted semantics for the first new feature stage

The first new feature stage should be **S035 — `View2D` Navigation Controller v1**.

### Public capability

Introduce an optional capability, for example:

```text
interaction.view2d.navigation.v1
```

This capability means the backend can accept protocol-owned 2D navigation actions and return coherent `View2D` updates. It does **not** mean the backend exposes native event streams, GUI callbacks, browser events, Datoviz controllers, Matplotlib widgets, or VisPy cameras.

### Controller ownership

A `View2DNavigationController` should be associated with exactly one target view/panel pair:

```text
controller_id
target_panel_id
target_view2d_id
enabled
current_view2d_revision
```

The controller owns no hidden rendering transform. Its only normative output is an explicit updated `View2D`.

### Minimal actions

Use semantic actions, not raw events:

```text
pan_by(dx_px, dy_px, layout_snapshot_id, view2d_revision)
zoom_about(anchor_px, factor_x, factor_y, layout_snapshot_id, view2d_revision)
set_view(view2d, previous_view2d_revision?)
reset_view(layout_snapshot_id?)
```

Recommended conventions:

* `dx_px`, `dy_px` are in the resolved panel viewport coordinate system, after layout.
* `anchor_px` is also in resolved panel viewport coordinates.
* `factor_x` and `factor_y` are finite positive values.
* A factor greater than `1` means zoom in: the visible data span is divided by that factor.
* Pan/zoom must be computed from the current accepted `View2D`, the resolved panel viewport, and the existing finite invertible 2D affine transform semantics.
* The result is a new explicit `View2D`, not a backend-private camera object.

### Minimal result object

Every action should return a structured result:

```text
accepted: bool
controller_id
old_view2d_revision
new_view2d_revision
view2d
layout_snapshot_id
diagnostics[]
```

If the action is accepted, `view2d` is the canonical new state.

If the action is rejected, diagnostics must explain why, for example:

```text
unsupported_capability
stale_view2d_revision
stale_layout_snapshot
non_finite_navigation_value
invalid_zoom_factor
non_invertible_view_transform
unsupported_live_input
```

### Render/query/readback coherence

This is the key acceptance criterion.

After a navigation update:

* render results must include the `view2d_revision` or `view_snapshot_id` used;
* query/readback results must include the same view/layout snapshot identifiers;
* stale input must be rejected or explicitly diagnosed;
* a query against a rendered result must be interpretable under the same `View2D` and layout snapshot;
* layout strictness still requires matching layout snapshot ids.

The controller is therefore just a deterministic state-update mechanism for `View2D`.

### Backend event adaptation

Backends may adapt native input to the protocol actions:

```text
native mouse drag  -> pan_by(...)
native wheel event -> zoom_about(...)
native reset key   -> reset_view(...)
```

But the native event itself is not public protocol data.

For S035, public semantics should **not** include:

```text
mouse down / move / up streams
keyboard binding tables
gesture recognizers
pointer capture
hover state
selection callbacks
inertia
kinetic scrolling
linked views
event bubbling/capture
DOM-style propagation
backend-native controller objects
```

Those can be added later only if there is a specific use case and a conformance story.

---

## 4. Explicit deferrals

### Defer from v0.1 release

Do not include these in the release blocker set:

* live pan/zoom;
* pointer/wheel/keyboard event protocol;
* controller state;
* linked navigation;
* public `View3D`;
* public 3D camera/projection;
* 3D mesh query;
* lighting/materials;
* backend-native interactive adapters.

The v0.1 release should be a clean static 2D baseline.

### Defer from S035

The `View2D` navigation stage should not define a general interaction system.

Defer:

* raw pointer event streams;
* raw wheel event streams;
* raw keyboard event streams;
* user callback dispatch;
* hover and selection semantics;
* picking;
* drag-box selection;
* brushing;
* lasso tools;
* linked views;
* synchronized axes;
* inertia;
* touch gestures;
* multi-pointer gestures;
* event propagation;
* focus management;
* cursor semantics;
* backend-native controller exposure.

S035 should only accept semantic navigation actions and return explicit `View2D` updates.

### Defer from S036

The first public 3D stage should be static camera/projection semantics, not a full 3D interaction or rendering model.

Minimal `View3D` should include:

```text
View3D
camera pose: eye, target/center, up
projection mode
projection parameters
viewport binding
near/far clipping
world→view→clip→panel transform
basic depth semantics for supported 3D visuals
snapshot/revision ids
capability-gated support for MeshVisual positions shaped (N,3)
```

Recommended projection scope:

* require **orthographic** first;
* allow **perspective** only if the stage is willing to define exact FOV/aspect/near/far semantics and fixtures;
* otherwise make perspective a follow-up capability such as `view3d.perspective.v1`.

Defer:

* orbit controller;
* trackball controller;
* fly camera;
* 3D pan/zoom gestures;
* arbitrary clipping planes;
* 3D mesh-local transforms;
* model/view hierarchy;
* scene graph ownership;
* material system;
* lighting;
* transparency ordering;
* shadows;
* volume rendering;
* 3D picking;
* ray/mesh intersection query;
* GPU buffer lifetime semantics;
* backend-native cameras;
* Datoviz/VisPy object exposure.

---

## 5. Risks and mitigations

### Risk: interactivity freezes the wrong abstraction

A broad event system would likely overfit to Matplotlib, Datoviz, VisPy, Qt, browser, or notebook assumptions.

**Mitigation:** S035 defines only semantic navigation actions and explicit `View2D` state transitions. Native events remain backend adapters.

### Risk: live backend behavior breaks query/readback coherence

If the backend changes its internal camera without the protocol knowing, rendered pixels and query results can diverge.

**Mitigation:** every accepted navigation action must return a new protocol-owned `View2D` revision. Render and query results must carry matching view/layout snapshot identifiers.

### Risk: Datoviz-native interaction leaks into public semantics

Datoviz can probably provide useful live behavior earlier than the protocol can standardize it.

**Mitigation:** allow Datoviz-native input as an adapted implementation detail only when it lowers to `pan_by`, `zoom_about`, `set_view`, or `reset_view`. Anything richer is experimental and not a public conformance claim.

### Risk: Matplotlib cannot be a strict live-interactivity reference

Matplotlib can support some interactive behavior, but backend GUI differences make strict live event conformance fragile.

**Mitigation:** require Matplotlib only for deterministic programmatic navigation fixtures initially. Live input support is capability-gated and may be reported unsupported.

### Risk: `View3D` becomes a graphics-engine API

A full camera/controller/material/light/scenegraph model would be too broad and premature.

**Mitigation:** S036 should define only static camera/projection/depth semantics needed for protocol-owned projection and `(N,3)` MeshVisual rendering. No orbit controller, lighting, materials, or object hierarchy.

### Risk: 3D query semantics are much harder than 2D query semantics

Mesh-local transforms, perspective unprojection, depth buffers, and ray intersections can quickly become underspecified.

**Mitigation:** S036 should require snapshot/readback identifiers and basic projection fixtures, but defer arbitrary 3D picking and mesh intersection query to a later stage.

---

## 6. Mission Control recommendation

Recommended mission sequence:

```text
S034 — v0.1 Static 2D Release Lock

Decision:
Release the approved 2D/static public API before adding interactivity or 3D.

Scope:
No new public feature semantics. Freeze the reviewed API shape, examples, capability matrix,
and structured unsupported diagnostics.

Acceptance:
The six reviewed examples remain passing across the intended backend matrix. Render/query/readback
results preserve layout snapshot coherence where strict layout is claimed. v0.1 release notes
explicitly mark interactivity and 3D as deferred.
```

```text
S035 — View2D Navigation Controller v1

Decision:
Add public pan/zoom only as protocol-owned semantic navigation actions that produce explicit
View2D updates.

Scope:
Define interaction.view2d.navigation.v1, controller target binding, pan_by, zoom_about, set_view,
reset_view, view revisioning, snapshot coherence, and structured diagnostics.

Acceptance:
Deterministic programmatic pan/zoom fixtures pass. Render/query/readback results report matching
view/layout snapshots after navigation. Native backend input may be adapted but is not public
protocol semantics.
```

```text
S036 — Minimal View3D Camera/Projection Baseline

Decision:
Add static protocol-owned View3D semantics after View2D navigation, narrowly enough to enable
capability-gated (N,3) MeshVisual use.

Scope:
Define View3D camera pose, projection parameters, viewport binding, near/far clipping, deterministic
projection math, basic depth semantics, snapshot ids, and structured unsupported diagnostics.

Acceptance:
Projection fixtures and simple 3D render/depth fixtures pass for at least one strict backend path.
MeshVisual (N,3) is accepted only under the View3D capability. Orbit control, 3D picking, lighting,
materials, and arbitrary clipping remain deferred.
```

**Release should happen before the first interactivity stage.** The approved 2D/static API is valuable and coherent now; interactivity should build on it as an additive, capability-gated v0.2-direction feature rather than destabilizing v0.1.
