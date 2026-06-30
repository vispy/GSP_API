# P022 - Datoviz View3D Camera Bindings And Orthographic API

This needs ChatGPT Pro consultation.

## Prompt

You are reviewing a Datoviz v0.4 and GSP_API integration decision. The goal is to decide the smallest correct Datoviz-side upgrade that lets GSP_API implement strict public View3D support through Datoviz without leaking Datoviz-specific API details into GSP.

Please answer as an architecture/API review, not as code generation. The expected output format is at the end.

### Project Context

GSP_API is a Python visualization protocol library with Matplotlib and Datoviz backends. It has an accepted first View3D slice:

- Public capability: `view3d.static.orthographic.v1`.
- Mesh capability: `meshvisual.positions3d.data.view3d.v1`.
- Query capability, deferred for Datoviz until render support exists: `query.view3d.ray_readback.v1`.
- Public View3D state is backend-neutral and camera-parameter-first:
  - `Camera3D(eye, target, up)`.
  - `OrthographicProjection3D(xlim, ylim, near_far)`.
  - `View3D(panel_id, camera, projection, revision)`.
- Orthographic `xlim` and `ylim` are explicit ordered bounds. Reversed x/y bounds are valid and tested.
- Off-axis bounds are valid and tested.
- GSP exposes projection snapshots for deterministic navigation/query semantics.
- GSP public protocol must not expose Datoviz names, matrices, Vulkan state, controller state, shader state, material structs, or slot names.

GSP currently supports View3D strictly in the Matplotlib reference path. Datoviz support is intentionally blocked with this diagnostic:

```text
mesh3d_coordinate_space_unsupported: Datoviz v0.4 MeshVisual strict adapter is limited to 2D positions until public View3D camera binding is implemented
```

### Current Datoviz Evidence

The local Datoviz checkout is v0.4-dev. The C API already exposes promising camera and mesh pieces.

Relevant Datoviz C declarations from `include/datoviz/controller/camera.h`:

```c
typedef enum
{
    DVZ_CAMERA_PERSPECTIVE = 0,
    DVZ_CAMERA_ORTHOGRAPHIC = 1,
} DvzCameraType;

typedef struct DvzCamera DvzCamera;

struct DvzCameraView
{
    vec3 eye;
    vec3 target;
    vec3 up;
};
typedef struct DvzCameraView DvzCameraView;

struct DvzCameraProjection
{
    DvzCameraType type;
    float fov_y;
    float near_clip;
    float far_clip;
    float ortho_height;
};
typedef struct DvzCameraProjection DvzCameraProjection;

struct DvzCameraDesc
{
    uint32_t struct_size;
    uint32_t flags;
    DvzCameraView view;
    DvzCameraProjection projection;
};
typedef struct DvzCameraDesc DvzCameraDesc;

DVZ_EXPORT DvzCameraView dvz_camera_view(void);
DVZ_EXPORT DvzCameraProjection dvz_camera_projection(void);
DVZ_EXPORT DvzCameraDesc dvz_camera_desc(void);
DVZ_EXPORT DvzCamera* dvz_camera_create(const DvzCameraDesc* desc);
DVZ_EXPORT void dvz_camera_set_view(DvzCamera* camera, const DvzCameraView* view);
DVZ_EXPORT void dvz_camera_get_view(const DvzCamera* camera, DvzCameraView* out);
DVZ_EXPORT void dvz_camera_set_perspective(
    DvzCamera* camera, float fov_y, float near, float far);
DVZ_EXPORT void dvz_camera_set_orthographic(
    DvzCamera* camera, float height, float near, float far);
DVZ_EXPORT void dvz_camera_resize(DvzCamera* camera, float width, float height);
DVZ_EXPORT void dvz_camera_mvp(DvzCamera* camera, DvzMVP* mvp);
DVZ_EXPORT void dvz_camera_destroy(DvzCamera* camera);
```

Relevant Datoviz C declarations from `include/datoviz/scene/camera.h`:

```c
DVZ_EXPORT DvzCamera* dvz_panel_set_camera(DvzPanel* panel, const DvzCameraDesc* desc);
DVZ_EXPORT DvzCamera* dvz_panel_camera(DvzPanel* panel);
```

Relevant Datoviz C declarations from scene/visual APIs:

```c
DVZ_EXPORT DvzVisualAttachDesc dvz_visual_attach_desc(void);
DVZ_EXPORT int dvz_panel_add_visual(
    DvzPanel* panel, DvzVisual* visual, const DvzVisualAttachDesc* desc);
DVZ_EXPORT int dvz_visual_set_depth_test(DvzVisual* visual, bool enabled);
DVZ_EXPORT DvzVisual* dvz_mesh(DvzScene* scene, uint32_t flags);
DVZ_EXPORT int dvz_mesh_set_geometry(DvzVisual* visual, const DvzGeometry* geometry);
DVZ_EXPORT int dvz_visual_set_index_data(
    DvzVisual* visual, const DvzIndex* indices, uint32_t index_count);
```

Relevant Datoviz controller/coordinate enum:

```c
typedef enum
{
    DVZ_CONTROLLER_APPLY = 0,
    DVZ_CONTROLLER_FIXED = 1,
    DVZ_CONTROLLER_APPLY_ISOTROPIC_LOCAL = 2,
    DVZ_CONTROLLER_APPLY_VIEW_PROJ = 3,
} DvzControllerMode;
```

`DvzVisualAttachDesc` has:

```c
struct DvzVisualAttachDesc
{
    uint32_t struct_size;
    uint32_t flags;
    int32_t z_layer;
    DvzControllerMode controller_mode;
    DvzVisualCoordSpace coord_space;
};
```

Datoviz C implementation of orthographic MVP currently computes a centered symmetric frustum:

```c
void dvz_camera_mvp(DvzCamera* camera, DvzMVP* mvp)
{
    glm_lookat(camera->eye, camera->target, camera->up, mvp->view);

    if (camera->type == DVZ_CAMERA_ORTHOGRAPHIC)
    {
        float height = camera->ortho_height > 0.0f ? camera->ortho_height :
                                                   DVZ_CAMERA_DEFAULT_ORTHO_HEIGHT;
        float width = height * camera->aspect;
        glm_ortho(
            -0.5f * width, +0.5f * width, -0.5f * height, +0.5f * height,
            camera->near_clip, camera->far_clip, mvp->proj);
    }
    else
    {
        float fov_y = camera->fov_y > 0.0f ? camera->fov_y : DVZ_CAMERA_DEFAULT_FOV_Y;
        glm_perspective(fov_y, camera->aspect, camera->near_clip, camera->far_clip, mvp->proj);
    }
}
```

### Current Datoviz Python Binding State

The raw Python ctypes generator is in `tools/bindings/generate_ctypes.py`.

It currently has this policy:

```python
def _unsupported_field_layout(type_info: dict) -> bool:
    for spelling in (type_info.get('qualtype', ''), type_info.get('canonical', '')):
        t = _clean_type(spelling)
        if t.startswith(('vec', 'dvec', 'mat')):
            return True
        if ('float[' in t or 'double[' in t) and '*' not in t:
            return True
    return False
```

Because of this, structs containing `vec3` or `mat4` are not emitted with usable `_fields_` unless forced and fully supported.

Observed Python ctypes state:

- `DvzCameraView` exists as a Python class but has no `_fields_`.
- `DvzCameraDesc` exists as a Python class but has no `_fields_`.
- `DvzCameraProjection` has usable `_fields_`: `type`, `fov_y`, `near_clip`, `far_clip`, `ortho_height`.
- `DvzMVP` exists as a Python class but has no `_fields_`.
- `dvz_camera_projection()` is exposed.
- `dvz_camera_view()` is skipped.
- `dvz_camera_desc()` is skipped.
- `dvz_camera_set_view()`, `dvz_camera_get_view()`, `dvz_camera_set_orthographic()`, `dvz_camera_resize()`, `dvz_camera_mvp()`, `dvz_panel_set_camera()`, and `dvz_panel_camera()` are exposed, but Python cannot safely fill the required structs.

The generated ABI facts report:

```text
DvzCameraView:
  size 36, align 4
  fields: eye 0, target 12, up 24

DvzCameraProjection:
  size 20, align 4
  fields: type 0, fov_y 4, near_clip 8, far_clip 12, ortho_height 16

DvzCameraDesc:
  size 64, align 4
  fields: struct_size 0, flags 4, view 8, projection 44

DvzMVP:
  size 208, align 16
  fields: model 0, view 64, proj 128, time 192, flags 196

DvzVisualAttachDesc:
  size 20, align 4
  fields: struct_size 0, flags 4, z_layer 8, controller_mode 12, coord_space 16
```

Current binding policy skip list includes:

```text
dvz_camera_desc
dvz_camera_view
```

### Candidate Datoviz Upgrade

A narrow binding-only upgrade could:

1. Teach the ctypes generator to map fixed math aliases:
   - `vec2` -> `ctypes.c_float * 2`
   - `vec3` -> `ctypes.c_float * 3`
   - `vec4` -> `ctypes.c_float * 4`
   - `dvec*` -> `ctypes.c_double * N`
   - `mat4` -> a ctypes layout matching C ABI, probably `(ctypes.c_float * 4) * 4`
2. Add `DvzCameraView`, `DvzCameraDesc`, and likely `DvzMVP` to the forced layout records policy.
3. Emit `dvz_camera_view()` and `dvz_camera_desc()` once their by-value return structs are layoutable.
4. Add ABI validation and smoke tests.

This would likely let Python set `eye`, `target`, `up`, create or update a panel camera, and inspect/generated MVP matrices.

However, it does not solve the semantic mismatch that Datoviz orthographic camera currently exposes only centered `height + aspect`, while GSP needs explicit ordered `xlim`, `ylim`, and `near_far`.

Possible API-level Datoviz upgrades:

Option A: add orthographic bounds API:

```c
DVZ_EXPORT void dvz_camera_set_orthographic_bounds(
    DvzCamera* camera,
    float left,
    float right,
    float bottom,
    float top,
    float near,
    float far);
```

Potential implications:
- Allows GSP `xlim`, `ylim`, reversed bounds, and off-axis bounds to lower directly.
- Requires internal `DvzCameraProjection` to carry bounds or flags.
- Need to decide whether reversed bounds are accepted in Datoviz camera API or whether GSP should normalize/reverse via model/view.

Option B: add projection-matrix API:

```c
DVZ_EXPORT void dvz_camera_set_projection_matrix(DvzCamera* camera, const mat4 projection);
```

Potential implications:
- Most flexible.
- More matrix-first and less semantic.
- GSP can keep matrices internal, but Datoviz public API would expose matrix control.
- Need to define interaction with `dvz_camera_mvp`, resize, perspective/orthographic type, and controller semantics.

Option C: keep Datoviz camera API unchanged and make GSP adapt:
- Use centered Datoviz orthographic only when GSP bounds are symmetric and unreversed.
- For off-axis/reversed bounds, CPU-transform data before upload or insert a model transform.
- Report adaptation diagnostics.

Potential implications:
- Smaller Datoviz change.
- Harder to claim strict retained View3D semantics.
- Risk of inconsistent query/readback and navigation behavior.

Option D: introduce a higher-level Datoviz View3D descriptor:

```c
typedef struct DvzView3DDesc
{
    uint32_t struct_size;
    uint32_t flags;
    vec3 eye;
    vec3 target;
    vec3 up;
    float left;
    float right;
    float bottom;
    float top;
    float near;
    float far;
} DvzView3DDesc;

DVZ_EXPORT int dvz_panel_set_view3d(DvzPanel* panel, const DvzView3DDesc* desc);
```

Potential implications:
- Best semantic match to GSP's first slice.
- Adds another abstraction alongside camera/controller APIs.
- Needs policy about perspective future expansion.

### Decision Questions

Please answer these directly:

1. Is a binding-only upgrade sufficient for GSP to honestly claim `view3d.static.orthographic.v1` through Datoviz, or is a Datoviz camera API extension required?
2. If an API extension is required, which shape is best for Datoviz v0.4: orthographic bounds API, projection matrix API, panel View3D descriptor, or another design?
3. Should Datoviz accept reversed orthographic bounds directly, or should GSP normalize reversed bounds before calling Datoviz? Explain the impact on deterministic parity and query/readback.
4. Should `DvzCameraProjection` itself grow explicit bounds fields, or should bounds be set through an additional API while preserving the existing struct layout?
5. What exact ctypes generator changes are safe for `vec*`, `dvec*`, and `mat4` fields, and what ABI tests are required?
6. What minimal Datoviz runtime tests should prove that a GSP DATA `(N,3)` mesh is actually camera-projected and depth-tested correctly?
7. What should remain explicitly out of scope for this upgrade so it does not accidentally become a full 3D material/light/scene-graph redesign?

### Expected Output Format

Return:

1. **Recommendation**: one concise paragraph with the chosen design.
2. **Datoviz C API Changes**: exact proposed structs/functions and compatibility notes.
3. **Python Binding Changes**: exact generator and policy changes, including math alias handling.
4. **GSP Integration Contract**: what GSP may claim after this lands, and what diagnostics remain.
5. **Tests**: a concrete checklist of Datoviz tests and GSP probe/review tests.
6. **Risks And Non-Goals**: explicit risks, rejected alternatives, and scope boundaries.

