# S037 Datoviz View3D Evidence

Status: M166 completed; Datoviz static public `(N, 3)` `MeshVisual` rendering is implemented for
local `v0.4-dev` builds that expose the P022 camera bindings.

## Probe Command

```bash
tools/probe_datoviz_view3d.py
```

The active import resolved to the local Datoviz checkout:

```text
/home/cyrille/GIT/Viz/datoviz/datoviz/__init__.py
```

The probe now reports `status: ready` when the local Datoviz branch contains:

- `DvzCameraView` with `eye`, `target`, and `up` ctypes fields;
- `DvzCameraDesc` with `view` and `projection` ctypes fields;
- `DvzCameraProjection` with `type`, `near_clip`, `far_clip`, and `ortho_height`;
- `dvz_camera_desc()`;
- `dvz_panel_set_camera()`;
- `dvz_camera_set_orthographic_bounds()` and `dvz_camera_get_orthographic_bounds()`;
- mesh upload and depth-test symbols.

## Datoviz Prerequisite Commits

The P022 prerequisites were added on Datoviz `v0.4-dev`:

- `83c1c8616 Add explicit orthographic camera bounds`
- `aeb8ecfe2 Expose camera ctypes layouts`
- `76b063d58 Guard input event ctypes layout`

## GSP Support Claim

GSP commit `38362fc Enable Datoviz View3D mesh rendering` implements the private lowering layer:

- `View3D.camera` lowers into Datoviz panel-owned camera state;
- `OrthographicProjection3D.xlim`, `.ylim`, and `.near_far` lower directly to explicit Datoviz
  orthographic bounds, including reversed x/y bounds;
- DATA `(N, 3)` meshes require `View3D`;
- NDC `(N, 3)` meshes are uploaded as panel NDC3;
- 3D meshes enable Datoviz depth testing;
- translucent 3D colors and 2D affine transforms on 3D meshes remain structured unsupported.

Validated examples:

```bash
uv run python examples/review/07_view3d_cube.py --backend datoviz --offscreen
uv run python examples/review/08_view3d_terrain.py --backend datoviz --offscreen
uv run python examples/review/09_view3d_ndc_depth.py --backend datoviz --offscreen
```

## Still Deferred

- Datoviz live `View3D` orbit/pan/zoom navigation.
- Datoviz GPU visual hit picking for 3D meshes.
- Public material, light, texture, UV, sampler, culling, perspective, and strict fragment-clipping
  semantics.

M167 adds `query.view3d.ray_readback.v1` for canonical ray-context payload generation. This uses
public `View3D` state and projection snapshots; it does not claim Datoviz GPU visual hit picking for
3D meshes.
