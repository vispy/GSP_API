# View3D Navigation Actions

Status: accepted S037 contract; protocol dataclasses and backend adapters are staged across S037
missions.

Semantic purpose: define backend-neutral `View3D` navigation actions that update canonical
`View3D` state. This spec does not expose backend-native event streams, trackball controllers,
Datoviz camera objects, or Matplotlib artist objects.

## Scope

Accepted S037 concepts:

| Concept | Status | Semantics |
|---|---:|---|
| Orbit | accepted | Rotate the camera eye around the target while preserving radius. |
| Pan | accepted | Translate camera eye and target in the view right/up plane. |
| Zoom | accepted | Scale orthographic projection bounds, optionally around a panel-NDC anchor. |
| Set camera | accepted | Replace canonical `Camera3D`. |
| Set projection | accepted | Replace canonical `OrthographicProjection3D`. |
| Reset | accepted | Restore explicit home camera/projection state. |
| Navigation result | accepted | New canonical `View3D`, revision, and projection snapshot identity. |
| Raw input events | deferred | Mouse, wheel, keyboard, touch, gesture, and backend-native event streams. |
| Backend controllers | private | Backend-native controllers may adapt into actions but are not public API. |

## Action Model

`View3DNavigationAction` fields:

| Field | Required | Semantics |
|---|---:|---|
| `kind` | yes | One of `orbit`, `pan`, `zoom`, `set_camera`, `set_projection`, `reset`. |
| `view_id` | yes | Target `View3D`. |
| `base_view_revision` | yes | Revision the action was computed against. |
| `base_layout_snapshot_id` | no | Required when panel-derived coordinates are used. |
| `base_view_projection_snapshot_id` | yes | Projection snapshot the action was computed against. |
| `payload` | yes | One of the payloads below. |

The canonical state is `View3D.camera` and `View3D.projection`. Navigation actions do not mutate
backend camera objects directly; they produce a new canonical `View3D`.

## Payload Semantics

### Orbit

Fields:

| Field | Required | Semantics |
|---|---:|---|
| `delta_yaw_radians` | yes | Finite yaw rotation around the view up axis. |
| `delta_pitch_radians` | yes | Finite pitch rotation around the view right axis. |
| `pivot` | no | `target` in S037. |
| `radius_policy` | no | `preserve` in S037. |

Orbit preserves the camera-target radius and keeps the target fixed. Resulting camera state must pass
`Camera3D` validation.

### Pan

Fields:

| Field | Required | Semantics |
|---|---:|---|
| `delta_view_right` | yes | Finite DATA-space offset along the derived view right vector. |
| `delta_view_up` | yes | Finite DATA-space offset along the derived true-up vector. |
| `units` | no | `data` in S037. |

Pan adds the same DATA-space offset to `camera.eye` and `camera.target`.

### Zoom

Fields:

| Field | Required | Semantics |
|---|---:|---|
| `scale` | yes | Finite positive scale; values greater than `1` zoom in. |
| `anchor_panel_ndc_xy` | no | Optional anchor in panel NDC x/y. |

Zoom scales orthographic `xlim` and `ylim`. If an anchor is provided, the DATA point under that
panel-NDC anchor remains under the anchor after zoom. Actions using anchors must provide a matching
layout snapshot id when layout strictness is claimed.

### Set Camera

Replaces `View3D.camera` with an explicit valid `Camera3D`.

### Set Projection

Replaces `View3D.projection` with an explicit valid `OrthographicProjection3D`.

### Reset

Restores explicit home/default `Camera3D` and `OrthographicProjection3D` values supplied by the
payload or controller configuration.

## Result Model

`View3DNavigationResult` fields:

| Field | Required | Semantics |
|---|---:|---|
| `accepted` | yes | Whether canonical state changed. |
| `view_id` | yes | Target view id. |
| `old_revision` | yes | Revision before action. |
| `new_revision` | yes if accepted | Revision after action. |
| `camera` | yes if accepted | New canonical `Camera3D`. |
| `projection` | yes if accepted | New canonical `OrthographicProjection3D`. |
| `layout_snapshot_id` | no | Layout snapshot used by the action. |
| `view_projection_snapshot_id` | yes if accepted | Fresh projection snapshot id. |
| `action_kind` | yes | Accepted or rejected action kind. |
| `diagnostics` | yes | Structured diagnostics. |

## Freshness Rules

- Any accepted camera/projection change increments `View3D.revision`.
- Every accepted navigation result recomputes `View3DProjectionSnapshot`.
- `base_view_revision` must match the current `View3D.revision`.
- `base_view_projection_snapshot_id` must match the current projection snapshot id.
- Layout-derived actions must match the current layout snapshot id.
- Query payloads after navigation must carry the new view revision and projection snapshot id.
- Old actions are rejected; no implicit rebase policy is accepted in S037.
- Degenerate camera/projection results are rejected and diagnosed rather than normalized silently.

## Diagnostics

Recommended diagnostics:

| Code | Meaning |
|---|---|
| `view3d_navigation_unsupported` | Backend or transport does not support View3D navigation. |
| `view3d_navigation_action_unsupported` | Action kind or payload is not supported. |
| `view3d_navigation_snapshot_mismatch` | Action references stale view/layout/projection snapshot state. |
| `view3d_navigation_invalid_delta` | Orbit or pan deltas are non-finite or invalid. |
| `view3d_navigation_invalid_zoom` | Zoom scale or anchor is invalid. |
| `view3d_navigation_invalid_result` | Resulting camera/projection state fails validation. |

## Capability

```text
view3d.navigation.orbit_pan_zoom.v1
```

A backend supports this capability when it accepts backend-neutral `View3DNavigationAction` values
for orbit, pan, zoom, reset, set-camera, and set-projection; validates base revisions and snapshot
ids; and returns a new canonical `View3D` state with a fresh revision and projection snapshot.

Native backend controller objects are not public API.

## Backend Mapping

Matplotlib is the reference adapter for deterministic action application and interactive review. It
may adapt mouse drag/wheel events into public actions, but Matplotlib callback ids, axes, and artist
objects are private.

Datoviz may use native camera or input machinery internally only if the resulting state is
synchronized into canonical `View3D` and passes the same revision/snapshot tests. Datoviz camera
objects, controller objects, and draw-state names are private.

VisPy2-style producers may provide ergonomic wrappers, but they must emit canonical actions and
consume canonical results.

## Deferred

Perspective navigation, raw event streams, pointer capture, key binding tables, trackball-specific
state, kinetic/gesture behavior, linked 3D views, 3D visual picking, materials, lights, textures,
scene graphs, and backend-native public controller exposure.
