## 1. Decision

**Choose A as the strict architecture.**

More precisely:

> **GSP strict 2D navigation should remain canonical `View2D` navigation, but the current approximate adapter must be replaced by a Datoviz-exact interaction profile that reproduces Datoviz v0.4-dev panzoom conventions, constants, normalization, pan, wheel zoom, right-drag zoom, and reset behavior.**

A **Datoviz-native controller path may exist only as a private, non-strict diagnostic/demo/oracle path**, not as the main implementation and not as public GSP navigation, unless and until Datoviz exposes enough state through Python bindings to synchronize every native interaction back into canonical `View2D` with strict snapshot guarantees.

So the practical decision is:

> **A is strict. B is not strict today. C is acceptable only if the “B” path is explicitly private and reported as non-strict/native/demo.**

---

## 2. Rationale

* **S035 already makes canonical `View2D` the authority.** The accepted model says strict backends adapt native input into semantic navigation actions and apply accepted `View2D` updates. Letting Datoviz native panzoom own the state would invert that model unless every native state change is read back and committed into `View2D`.

* **The current GSP adapter is structurally right but mathematically wrong.** It already converts native pointer input into canonical actions, but its `zoom_base=1.1`, wheel exponent, and right-drag scaling are approximate. Replace the math, not the architecture.

* **Datoviz-exact feel can be achieved without exposing Datoviz-native controllers.** The mouse conventions and formulas are fully expressible as private backend/input-profile logic that produces canonical `View2D` updates.

* **B is not currently feasible as the strict path from the facts given.** The prompt gives evidence that GSP can set Datoviz panel domains and view2d state, but not that Python bindings expose complete `DvzPanzoom` state, visible extent, or post-interaction callbacks sufficient for strict synchronization.

* **Axis synchronization is cleaner if `View2D` is authoritative.** Data visuals, guides, axes, query/readback, and render snapshots can all consume the same committed `View2D`. With native Datoviz panzoom as owner, axes risk lagging or diverging unless readback is perfect.

* **Legacy `AxesDisplay` / `AxesPanZoom` conflicts with the accepted model.** It owns independent limits and rebuilds axes only through legacy calls like `set_limits_dunit()`. It should be deleted or rewritten as a guide renderer consuming canonical `View2D`, not adapted around.

* **Avoiding stale Datoviz formulas is a testing/versioning problem, not a reason to abandon canonical state.** Pin the exact Datoviz-derived profile, verify it against Datoviz source/native behavior where possible, and update it deliberately when Datoviz changes.

* **Public GSP APIs should remain backend-neutral.** Public concepts should be `View2D`, semantic navigation actions, guide synchronization, and strict snapshot identity — not `DvzPanzoom`, `dvz_view_panzoom()`, or Datoviz controller state.

---

## 3. Axis synchronization model

**Authoritative state:** canonical GSP `View2D`.

Not authoritative:

* Datoviz panel domain.
* Datoviz native axes.
* legacy `AxesDisplay` limits.
* legacy `AxesPanZoom` state.
* backend-native controller state.

The strict update pipeline should be:

1. Native backend input event occurs: mouse drag, wheel, double click, resize.
2. Backend-specific raw event adapter normalizes it into the private GSP interaction profile.
3. The Datoviz-exact profile computes a semantic S035 action:

   * left drag → canonical pan update;
   * right drag → canonical x/y zoom-about update;
   * wheel → canonical zoom-about update;
   * double click → `reset_view`.
4. The navigation reducer applies the action to the previous canonical `View2D`.
5. A new accepted `View2D` snapshot is committed.
6. Data visuals and guides/axes consume that same snapshot.
7. Renderer applies the committed snapshot to backend state:

   * Datoviz: `dvz_panel_set_domain(panel, X/Y, min, max)` and `dvz_panel_set_view2d(...)`;
   * Matplotlib: set `Axes.set_xlim`, `Axes.set_ylim`, redraw guides/ticks from the same state.
8. Render/query/readback records the matching `view_snapshot_id` and `layout_snapshot_id`.

`configure_view2d_axes()` should stop being a one-time initialization endpoint. It should be split conceptually into:

* **axis creation/configuration:** create native axes, labels, grid policy, tick policy;
* **axis update:** recompute or refresh ticks, domains, labels, and grid from the current `View2D`.

On every accepted navigation update:

```text
canonical View2D changes
        ↓
data transform/domain changes
        ↓
axis/guide limits and ticks recompute
        ↓
render uses one coherent snapshot
```

On resize:

* the canonical data domain normally stays unchanged;
* panel pixel geometry changes;
* tick density/layout may change;
* future mouse normalization must use the new panel width/height;
* axes/guides should recompute from the same `View2D` plus the new layout snapshot.

The legacy model:

```text
AxesPanZoom owns panzoom
AxesDisplay owns limits
View2D separately owns navigation
```

should be removed.

---

## 4. Datoviz parity plan

Define one private implementation profile, for example internally named:

```text
_GSPDatovizPanzoomV04Profile
```

or similar. It should encode the Datoviz v0.4-dev behavior from the audited source evidence:

```c
DVZ_PANZOOM_ZOOM_MIN_DEFAULT = 1e-3f
DVZ_PANZOOM_ZOOM_MAX_DEFAULT = 1e+4f

Apple:
  DRAG_COEF  = .003
  WHEEL_COEF = 12.0

Other platforms:
  DRAG_COEF  = .002
  WHEEL_COEF = 120.0
```

Coordinate normalization must match Datoviz:

```c
pos_x = -1.0 + 2.0 * px / w
pos_y = +1.0 - 2.0 * py / h

shift_x = +2.0 * dx / w
shift_y = -2.0 * dy / h
```

Pan must match:

```c
pan_x = pan_center_x + shift_x / zoom_x
pan_y = pan_center_y + shift_y / zoom_y
```

Right-drag zoom must match:

```c
a = 0.5 * (w + h)

zoom_x = zoom_center_x * exp(DRAG_COEF * a * normalized_shift_x)
zoom_y = zoom_center_y * exp(DRAG_COEF * a * normalized_shift_y)

px = center_x * (1 / zoom_center_x - 1 / zoom_x) * zoom_x
py = center_y * (1 / zoom_center_y - 1 / zoom_y) * zoom_y

pan_x = pan_center_x - px / zoom_x
pan_y = pan_center_y - py / zoom_y
```

Wheel zoom must match:

```c
a = h / w
d = dir_y / 4.0

shift_x = WHEEL_COEF * d
shift_y = -a * shift_x
```

Then apply the same zoom-shift semantics as Datoviz.

Important implementation choice:

* The internal profile may use a private Datoviz-like `(pan, zoom)` state as an intermediate.
* The committed public state must still be canonical `View2D`.
* The private `(pan, zoom)` state must never become a public GSP object.

To avoid silent drift when Datoviz changes:

1. Pin the profile to the audited Datoviz version/commit in comments and diagnostics.
2. Add golden tests for the formulas.
3. Add optional parity tests against a local Datoviz checkout or native test binary when available.
4. Treat future Datoviz formula changes as a deliberate spec/ADR update, not an accidental backend behavior change.
5. If future Python bindings expose native panzoom state cleanly, the backend may use Datoviz native code privately as the calculation engine, but only if every interaction still commits a canonical `View2D` snapshot immediately.

---

## 5. API/capability boundary

Public GSP concepts should remain:

```text
View2D
pan_by
zoom_about
set_view
reset_view
strict_view2d_navigation
guide synchronization
view/layout snapshots
```

Public GSP should not expose:

```text
DvzPanzoom
dvz_view_panzoom()
Datoviz pointer callbacks
Datoviz controller state
raw wheel/pointer/touch events as protocol objects
legacy AxesPanZoom
legacy AxesDisplay limits
```

Suggested public capability names:

```text
view2d.navigation.strict = true
view2d.navigation.semantic_actions = true
view2d.navigation.pointer_profile = "gsp_2d_v1"
view2d.guides.synchronized = true | false
view2d.snapshots.render_view_layout = true | false
```

The phrase `Datoviz` may appear in diagnostics/provenance, but not as a public protocol dependency. For example:

```text
diagnostics.navigation_profile_provenance =
  "gsp_2d_v1 derived from Datoviz panzoom v0.4-dev commit 32ad98848"
```

If a native Datoviz controller path is kept, it should be named diagnostically as something like:

```text
backend_native_navigation_demo
```

or:

```text
native_unsynchronized_navigation
```

and must report:

```text
strict = false
reason = "native controller state is not committed as canonical View2D after each interaction"
```

Do not name the public capability after `DvzPanzoom`.

---

## 6. Implementation steps

1. **Amend/clarify S035 implementation notes** to state that GSP strict 2D interaction uses a canonical Datoviz-derived `gsp_2d_v1` pointer profile.

2. **Replace `View2DNavigationInputAdapter` math.**
   Remove `zoom_base=1.1` as the strict/default behavior. Implement Datoviz-exact normalization, pan, wheel zoom, right-drag zoom, reset, min/max zoom clamps, and platform constants.

3. **Keep S035 semantic actions.**
   The adapter should still emit/apply `PanByAction`, `ZoomAboutAction`, `SetViewAction`, or `ResetViewAction`, or their accepted internal equivalents. Do not expose raw events.

4. **Disable Datoviz native panzoom in strict mode.**
   `_DatovizLiveView2DNavigation` should continue subscribing to Datoviz pointer input, but it should not delegate ownership to `dvz_view_panzoom()` for strict GSP navigation.

5. **Refactor axis handling.**
   Split `configure_view2d_axes()` into creation/configuration and per-view update. Axis domains, ticks, grids, and labels must update from each accepted `View2D`.

6. **Delete or rewrite legacy axes/panzoom.**
   Remove `vispy2.axes.AxesPanZoom` from the strict path. Replace `AxesDisplay` with a guide/axis renderer that consumes canonical `View2D`. Do not preserve `set_limits_dunit()` as an authority.

7. **Unify Matplotlib and Datoviz behavior.**
   Matplotlib strict interaction should use the same GSP semantic profile rather than Matplotlib’s native toolbar/navigation behavior.

8. **Add snapshot bookkeeping.**
   Every render/query/readback claiming strictness should identify the accepted `View2D` and layout snapshot used by both data and guides.

9. **Add capability reporting.**
   Report strict navigation only when canonical updates, data visuals, and guide/axis updates are synchronized.

10. **Document migration.**
    Mark the old axes/panzoom helpers as removed/replaced, not compatibility-preserved.

---

## 7. Tests/proofs

1. **Formula unit tests**

   * `_normalize_pos`
   * `_normalize_shift`
   * left-drag pan
   * right-drag x/y zoom
   * wheel zoom
   * zoom min/max clamp
   * double-click reset

2. **Golden interaction traces**
   Use fixed panel sizes, pointer positions, drags, wheel deltas, and initial views. Assert final canonical `View2D` against golden values.

3. **Platform constant tests**
   Verify Apple and non-Apple coefficient selection separately. Do not let CI host OS silently change expected values without explicit parametrization.

4. **Cross-backend strictness tests**
   Feed the same semantic interaction trace to Matplotlib and Datoviz. Assert identical accepted `View2D` snapshots within tolerance.

5. **Axis synchronization tests**
   After pan, wheel zoom, right-drag zoom, reset, and resize:

   * data domain changes;
   * axes limits change;
   * ticks/grid correspond to the same `View2D`;
   * no stale legacy limits remain.

6. **Render/query snapshot tests**
   Assert that rendered data and rendered guides report the same `view_snapshot_id` and compatible `layout_snapshot_id`.

7. **Legacy isolation tests**
   Ensure strict navigation does not instantiate or call `AxesPanZoom`, legacy viewport-event panzoom, or `AxesDisplay.set_limits_dunit()`.

8. **Optional Datoviz-native oracle smoke**
   When a local Datoviz checkout or sufficient bindings are available, run the same traces against native Datoviz panzoom and compare the resolved visible extent to GSP’s canonical `View2D`.

9. **Capability tests**
   A backend must not report strict guide/navigation support unless navigation state and axes/guides are synchronized through canonical `View2D`.

---

## 8. Risks/open questions

* **Exact wheel semantics depend on native event units.** The Datoviz formula uses `dir[1] / 4.0`; GSP must ensure backend wheel deltas are normalized to the same units before applying the formula.

* **Float precision may matter.** Datoviz uses C `float`; Python math uses double by default. Tests should define tolerances, or the implementation should cast through `float32` where needed for closer parity.

* **Datoviz native axes may not auto-refresh on domain updates.** If `dvz_panel_set_domain()` does not force tick/grid recomputation, GSP must explicitly refresh/recreate guide state after each committed `View2D`.

* **The profile is version-specific.** “Datoviz-exact” should mean exact for the pinned Datoviz v0.4-dev behavior. Future Datoviz changes require an intentional profile/spec update.

* **Native-controller strictness is blocked unless readback is complete.** B can become viable only if Python bindings expose enough native panzoom state or visible-domain resolution to commit canonical `View2D` after every interaction.

* **Trackpad/high-resolution wheel behavior may expose edge cases.** The adapter should test discrete mouse wheels and continuous scroll devices separately.

* **Deleting legacy helpers may break examples/tests.** That is acceptable under the stated constraint, but the migration should be direct: examples should move to canonical `View2D` guides, not compatibility wrappers.

