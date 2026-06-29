# View2D Navigation Actions

Status: accepted S035 baseline.

Semantic purpose: add deterministic 2D pan/zoom navigation by applying semantic actions to `View2D`
state. S035 does not define a general event system.

## Scope

Accepted S035 concepts:

| Concept | Status | Semantics |
|---|---:|---|
| `View2DNavigationController` | accepted | Optional state holder targeting one panel and one `View2D`. |
| `pan_by` | accepted | Pan a view by a resolved logical-pixel delta. |
| `zoom_about` | accepted | Zoom around a resolved logical-pixel anchor. |
| `set_view` | accepted | Replace the target `View2D` with explicit limits. |
| `reset_view` | accepted | Restore a configured home/default `View2D`. |
| Navigation result | accepted | Structured accepted/rejected result with updated `View2D` and diagnostics. |
| Raw input events | deferred | Mouse, wheel, keyboard, touch, gesture, and backend-native event streams. |
| Public 3D navigation | deferred | `View3D`, camera, projection, orbit, trackball, and 3D picking. |

## Controller Model

A `View2DNavigationController` targets exactly one panel/view pair:

| Field | Required | Semantics |
|---|---:|---|
| `id` | yes | Stable controller id. |
| `panel_id` | yes | Target panel receiving navigation. |
| `view_id` | yes | Target `View2D`. |
| `enabled` | no | Disabled controllers reject actions with diagnostics. |
| `home_view` | no | Optional reset target. |
| `current_view2d_revision` | yes | Revision token for stale-action detection. |

The controller owns no hidden camera, backend widget, or transform stack. Its normative output is a
new explicit `View2D`.

## Action Semantics

Coordinates are in resolved panel logical pixels, using the layout snapshot named by the action when
layout is available. The panel rectangle maps linearly to panel NDC:

```text
panel_ndc_x = -1 + 2 * (px_x - rect_x) / rect_width
panel_ndc_y = -1 + 2 * (px_y - rect_y) / rect_height
```

### `pan_by`

Fields:

| Field | Required | Semantics |
|---|---:|---|
| `dx_px` | yes | Horizontal logical-pixel delta. |
| `dy_px` | yes | Vertical logical-pixel delta. |
| `layout_snapshot_id` | yes if layout strict | Snapshot defining the panel rectangle. |
| `view2d_revision` | yes | Revision the action was computed against. |

Dragging content to the right increases the visible data limits by the negative panel movement in
data units. For a panel rectangle of width `w` and height `h`:

```text
data_dx = -dx_px / w * (xlim[1] - xlim[0])
data_dy = -dy_px / h * (ylim[1] - ylim[0])
new_xlim = (xlim[0] + data_dx, xlim[1] + data_dx)
new_ylim = (ylim[0] + data_dy, ylim[1] + data_dy)
```

This formula preserves reversed limits because the span may be negative.

### `zoom_about`

Fields:

| Field | Required | Semantics |
|---|---:|---|
| `anchor_px` | yes | Logical-pixel anchor in the target panel. |
| `factor_x` | yes | Finite positive x zoom factor. Values greater than `1` zoom in. |
| `factor_y` | yes | Finite positive y zoom factor. Values greater than `1` zoom in. |
| `layout_snapshot_id` | yes if layout strict | Snapshot defining the panel rectangle. |
| `view2d_revision` | yes | Revision the action was computed against. |

The anchor maps to a data coordinate under the current `View2D`; after zoom, that data coordinate
remains under the same anchor pixel.

For an anchor fraction `tx = (anchor_x - rect_x) / rect_width`:

```text
anchor_data_x = xlim[0] + tx * (xlim[1] - xlim[0])
new_span_x = (xlim[1] - xlim[0]) / factor_x
new_xlim = (anchor_data_x - tx * new_span_x, anchor_data_x + (1 - tx) * new_span_x)
```

Y uses the same rule with `ty`, `ylim`, and `factor_y`. Reversed limits are preserved by signed spans.

### `set_view`

`set_view` replaces the target `View2D` with explicit finite non-zero-span x/y limits. It follows
the same validation rules as S027 `View2D`.

### `reset_view`

`reset_view` restores `home_view` if present. If no home view exists, the action is rejected with a
diagnostic.

## Result Model

Every action returns a structured result:

| Field | Required | Semantics |
|---|---:|---|
| `accepted` | yes | Whether the action changed the canonical view state. |
| `controller_id` | yes | Navigation controller id. |
| `old_view2d_revision` | yes | Input/current revision before action. |
| `new_view2d_revision` | yes if accepted | Revision after action. |
| `view` | yes if accepted | Canonical new `View2D`. |
| `view_snapshot_id` | no | Snapshot id used by render/query/readback. |
| `layout_snapshot_id` | no | Layout snapshot used for pixel-to-data conversion. |
| `diagnostics` | yes | Structured diagnostics. |

Recommended diagnostics:

| Code | Meaning |
|---|---|
| `GSP_NAVIGATION_UNSUPPORTED` | Backend or transport does not support the requested navigation capability. |
| `GSP_NAVIGATION_DISABLED` | Controller is disabled. |
| `GSP_NAVIGATION_STALE_VIEW` | Action references an old `View2D` revision. |
| `GSP_NAVIGATION_STALE_LAYOUT` | Action references an old layout snapshot. |
| `GSP_NAVIGATION_NONFINITE` | Delta, anchor, factor, or resulting limit is non-finite. |
| `GSP_NAVIGATION_INVALID_ZOOM_FACTOR` | Zoom factor is not finite and positive. |
| `GSP_NAVIGATION_INVALID_PANEL_RECT` | Panel rectangle has zero or invalid width/height. |
| `GSP_NAVIGATION_RESET_UNAVAILABLE` | `reset_view` requested without a home view. |

## Render and Query Coherence

After an accepted navigation action:

- render results must identify the `View2D` revision or view snapshot used;
- query/readback results must identify the same view/layout snapshot where strictness is claimed;
- stale actions must be rejected or explicitly diagnosed;
- guides and data visuals must consume the same accepted `View2D` snapshot;
- layout-strict results must carry a matching `layout_snapshot_id`.

## Backend Mapping

Matplotlib is the strict reference backend for deterministic programmatic behavior. Live GUI input is
optional and must be capability-reported separately.

Datoviz and other retained GPU backends should lower accepted `View2D` updates to panel
domain/view/projection or equivalent data-to-clip uniform/state updates. In the strict fast path,
unchanged visual data must not be re-uploaded and visual objects must not be recreated during
pan/zoom.

CPU remapping of finite eager arrays is allowed only as an explicit adapted fallback and must not be
advertised as the high-performance retained navigation path.

VisPy2 producer APIs may expose convenient mouse/wheel adapters, but they must lower to S035
navigation actions and `View2D` updates.

## Input Adapter and Review Paths

S035 includes a small backend-neutral pointer adapter for review and backend integration. The adapter
accepts resolved target-panel logical-pixel pointer events and emits only semantic `pan_by` or
`zoom_about` actions. Backends are still responsible for applying accepted results to their native
view state.

Supported in this stage:

| Path | Status | Notes |
|---|---:|---|
| Matplotlib native drag/wheel review | supported | `examples/protocol_view2d_navigation.py --backend matplotlib` adapts Matplotlib mouse events to S035 actions. |
| Matplotlib scripted smoke | supported | `examples/protocol_view2d_navigation.py --backend matplotlib --scripted-smoke` runs headless. |
| Datoviz retained scripted smoke | supported | `tools/s035_navigation_smoke.py --backend datoviz-fake` verifies retained update calls and no unchanged visual-buffer reupload. |
| Datoviz v0.4 pointer callback review | supported | `examples/protocol_view2d_navigation.py --backend datoviz` adapts Datoviz pointer events to S035 actions, then applies accepted `View2D` updates through the retained panel path. |
| Datoviz native panzoom controller | native-only demo | `dvz_view_panzoom()` may be used for backend-native experiments, but it is not strict GSP navigation unless its state is synchronized back into canonical `View2D`. |
| Public cross-backend event system | deferred | S035 intentionally keeps raw input streams outside the public protocol. |

Performance smoke command:

```bash
uv run python tools/s035_navigation_smoke.py --backend both --steps 40 --points 25000
```

The smoke report records navigation update count, frame/draw count where applicable, retained
update calls, and visual upload/recreation calls observed after the initial scene upload.

## Deferred

S035 defers raw event streams, key-binding tables, pointer capture, hover, selection, brushing,
lasso tools, linked navigation, synchronized axes, kinetic scrolling, touch gestures, event
propagation, focus/cursor semantics, public backend-native controller objects, public `View3D`,
camera/projection semantics, orbit/trackball controllers, and 3D picking.
