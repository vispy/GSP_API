# S037 Datoviz View3D Evidence

Status: M165 completed; Datoviz public `(N, 3)` `MeshVisual` support remains unsupported.

## Probe Command

```bash
tools/probe_datoviz_view3d.py
```

## Observed Environment

The active import resolved to the local Datoviz checkout:

```text
/home/cyrille/GIT/Viz/datoviz/datoviz/__init__.py
```

The module exposes several promising v0.4 camera and depth symbols, including:

- `DvzCamera`
- `DvzCameraProjection`
- `dvz_camera_create`
- `dvz_camera_set_view`
- `dvz_camera_set_orthographic`
- `dvz_camera_mvp`
- `dvz_panel_set_camera`
- `dvz_panel_camera`
- `dvz_mesh`
- `dvz_visual_set_depth_test`

Header evidence under `/home/cyrille/GIT/Viz/datoviz/include/datoviz/` confirms that C headers
define `DvzCameraView`, `DvzCameraProjection`, `DvzCameraDesc`, panel-owned cameras, and retained
visual depth-test APIs.

## Blocking Binding Gaps

The Python-visible binding is not sufficient to implement public GSP `View3D` semantics safely yet:

| Evidence | Status | Impact |
|---|---:|---|
| `DvzCameraView` eye/target/up fields | missing from Python `_fields_` | Cannot safely lower canonical `Camera3D(eye, target, up)` into Datoviz. |
| `DvzCameraDesc` view/projection fields | missing from Python `_fields_` | Cannot safely create or set a panel camera from public GSP state. |
| `dvz_camera_view()` default factory | not exposed | No safe Python-side default constructor for `DvzCameraView`. |
| `dvz_camera_desc()` default factory | not exposed | No safe Python-side default constructor for `DvzCameraDesc`. |
| Orthographic x/y bounds | Datoviz camera API exposes height/near/far | S036 requires explicit `xlim`, `ylim`, reversed x/y bounds, off-axis bounds, and deterministic panel-NDC3 parity. |
| Runtime DATA/NDC3/depth screenshots | not proven | Cannot claim retained `(N, 3)` support or opaque-depth capability. |

`DvzCameraProjection` does expose fields including `type`, `near_clip`, `far_clip`, and
`ortho_height`, but that is not enough to encode the accepted S036 projection contract.

## Decision

Keep the current Datoviz diagnostic for public `(N, 3)` meshes:

```text
mesh3d_coordinate_space_unsupported: Datoviz v0.4 MeshVisual strict adapter is limited to 2D positions until public View3D camera binding is implemented
```

Do not proceed to M166 implementation until Datoviz exposes either:

- Python-visible `DvzCameraView` and `DvzCameraDesc` fields/factories sufficient to set
  `eye`, `target`, `up`, orthographic projection, and panel camera state; or
- a higher-level public binding that directly accepts equivalent camera/projection state and can be
  tested against canonical S036 projection snapshots.

## Evidence Needed Before Support Claim

- DATA `(N, 3)` retained mesh moves correctly when canonical camera/projection changes.
- NDC `(N, 3)` retained mesh is interpreted directly as panel NDC3, not camera-projected DATA.
- Opaque nearer triangles win independent of submission order.
- Projection snapshot ids match canonical S036 state changes.
- Query ray-readback payloads match canonical S036 CPU snapshot semantics before
  `query.view3d.ray_readback.v1` is claimed.
- Public API remains free of Datoviz camera, controller, draw-state, and material names.
