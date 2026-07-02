# S047 Perspective View3D Direction

Status: accepted direction after user feedback and local Datoviz source inspection.

## Decision

Perspective `View3D` should become the primary next 3D protocol slice. Orthographic remains useful
as a deterministic/debug projection and for existing S036/S044 fixtures, but it should not be the
only serious 3D camera model.

## Rationale

- Real 3D examples and interactive work need perspective projection.
- Datoviz already has native perspective camera support:
  - `DvzCameraProjection.type = DVZ_CAMERA_PERSPECTIVE`;
  - `DvzCameraProjection.fov_y`;
  - `dvz_camera_set_perspective(camera, fov_y, near, far)`;
  - `dvz_panel_view3d_state()` readback exposes the camera projection.
- GSP currently hard-codes `OrthographicProjection3D` in `View3D`, navigation result payloads,
  projection snapshots, CPU projection/unprojection helpers, and tests. The right fix is a public
  projection-union protocol, not a backend-only Datoviz shortcut.

## Public Protocol Shape

Add a new projection dataclass, tentatively:

```python
@dataclass(frozen=True, slots=True)
class PerspectiveProjection3D:
    fov_y_degrees: float = 45.0
    near_far: tuple[float, float] = (0.1, 1000.0)
    aspect_ratio: float | None = None
    kind: Projection3DKind = Projection3DKind.PERSPECTIVE
```

`View3D.projection` should accept:

```python
OrthographicProjection3D | PerspectiveProjection3D
```

`aspect_ratio=None` means the renderer resolves aspect from the active panel/frame snapshot. A fixed
positive aspect ratio is allowed for deterministic tests and non-layout contexts.

Use an explicit unit-bearing field name (`fov_y_degrees`) in the public API. Datoviz can lower to
radians privately.

## Capability Gates

Add:

```text
view3d.static.perspective.v1
```

This should be separate from:

```text
view3d.static.orthographic.v1
view3d.navigation.orbit_pan_zoom.v1
query.view3d.ray_readback.v1
query.view3d.mesh_triangle_pick.v1
```

A backend may claim `view3d.static.perspective.v1` only when it can render public
`Camera3D + PerspectiveProjection3D` state without exposing backend-native camera/controller objects.

## Implementation Order

1. Protocol model:
   - add `Projection3DKind.PERSPECTIVE`;
   - add `PerspectiveProjection3D`;
   - widen `View3D.projection`, `SetProjection3DPayload`, `ResetView3DPayload`, and
     `View3DNavigationResult.projection`.
2. Math:
   - implement perspective project/unproject helpers;
   - resolve aspect ratio from explicit projection state or layout/frame context;
   - keep orthographic behavior unchanged.
3. Matplotlib:
   - use the perspective CPU reference/adapted path for examples and tests;
   - keep strict GPU-depth claims off.
4. Datoviz:
   - lower `PerspectiveProjection3D` via `dvz_panel_set_view3d_desc()` /
     `dvz_camera_set_perspective()`;
   - read back with `dvz_panel_view3d_state()`;
   - advertise `view3d.static.perspective.v1` only after retained DATA-space mesh and snapshot
     tests pass.
5. Examples:
   - switch serious 3D examples to perspective by default;
   - keep orthographic examples for deterministic debugging/ray/pick fixtures.

## Deferred From First Perspective Slice

- Perspective mesh triangle picking.
- Perspective live navigation capability promotion.
- Public arbitrary projection matrices.
- Public backend-native controllers.
- Nonlinear/depth-buffer readback guarantees beyond bounded ray-context tests.

## Impact On Datoviz Navigation Decision

Perspective strengthens the P029 conclusion. Datoviz native turntable is a better long-term match for
perspective orbit/pan/dolly than the direct Python reducer. For perspective cameras, wheel interaction
may be modeled as camera dolly rather than orthographic projection-bound zoom, but the public
navigation spec must say that explicitly before `view3d.navigation.orbit_pan_zoom.v1` is advertised
for perspective.
