## 1. **Recommendation**

A binding-only upgrade is **necessary but not sufficient**: it unlocks Python access to camera structs, but it cannot honestly support GSP’s strict `view3d.static.orthographic.v1` because Datoviz currently only exposes a centered orthographic projection derived from `height + aspect`, while GSP requires explicit ordered `xlim`, `ylim`, `near_far`, including off-axis and reversed x/y bounds. The smallest correct Datoviz-side upgrade is: **fix the ctypes math-struct bindings and add a camera-level orthographic-bounds API**, not a projection-matrix API and not a panel-level `View3D` abstraction. That keeps GSP camera-parameter-first, preserves Datoviz’s camera abstraction, and avoids leaking Datoviz matrices/controller/shader details into GSP.  

## 2. **Datoviz C API Changes**

Add a **camera-level orthographic bounds setter**, with bounds passed directly and ordered exactly as supplied:

```c
DVZ_EXPORT int dvz_camera_set_orthographic_bounds(
    DvzCamera* camera,
    float left,
    float right,
    float bottom,
    float top,
    float near_clip,
    float far_clip);
```

I would also add a getter for tests, diagnostics, and future internal validation:

```c
DVZ_EXPORT int dvz_camera_get_orthographic_bounds(
    const DvzCamera* camera,
    float* out_left,
    float* out_right,
    float* out_bottom,
    float* out_top,
    float* out_near_clip,
    float* out_far_clip);
```

The implementation should store an internal orthographic mode on `DvzCamera`, for example conceptually:

```c
enum
{
    DVZ_CAMERA_ORTHO_CENTERED = 0,
    DVZ_CAMERA_ORTHO_BOUNDS = 1,
};
```

That mode does **not** need to be public. Internally, `DvzCamera` should keep:

```c
float ortho_left;
float ortho_right;
float ortho_bottom;
float ortho_top;
bool ortho_has_bounds;
```

Then `dvz_camera_mvp()` should branch as follows:

```c
if (camera->type == DVZ_CAMERA_ORTHOGRAPHIC)
{
    if (camera->ortho_has_bounds)
    {
        glm_ortho(
            camera->ortho_left,
            camera->ortho_right,
            camera->ortho_bottom,
            camera->ortho_top,
            camera->near_clip,
            camera->far_clip,
            mvp->proj);
    }
    else
    {
        /* existing centered height + aspect behavior */
    }
}
```

Compatibility notes:

* `dvz_camera_set_orthographic(camera, height, near, far)` remains unchanged and keeps the current centered, aspect-scaled behavior.
* `dvz_camera_set_orthographic_bounds(...)` sets `camera->type = DVZ_CAMERA_ORTHOGRAPHIC`, records `near_clip` and `far_clip`, and enables bounds mode.
* `dvz_camera_set_perspective(...)` should clear bounds mode.
* `dvz_camera_resize(...)` should still update `aspect`, but in bounds mode it must **not** rewrite `left/right/bottom/top`; explicit bounds are the projection snapshot.
* `left == right`, `bottom == top`, and `near_clip == far_clip` should be rejected or asserted as invalid. Reversed x/y bounds must be accepted.
* Do **not** grow `DvzCameraProjection` for v0.4. It is embedded in `DvzCameraDesc`, so growing it changes public struct size/offsets and complicates ABI compatibility. Preserve the existing `DvzCameraProjection` layout and set explicit bounds through the additional API. The current public declarations and ABI facts show that `DvzCameraDesc` and `DvzCameraProjection` are already part of the C/Python boundary.  

Datoviz should accept reversed orthographic x/y bounds directly. GSP’s ordered bounds are semantic state, not merely a normalized extent. Normalizing in GSP and compensating with CPU transforms or hidden model transforms would make the rendered image harder to reason about, and it would become especially fragile for deterministic projection snapshots, future ray queries, readback, clipping, winding/culling behavior, and backend parity. Directly lowering `xlim[0], xlim[1], ylim[0], ylim[1]` into the camera projection is the cleanest strict contract.

Rejected C API shapes:

* **Projection matrix API**: too matrix-first for this slice. It creates unresolved semantics around resize, camera type, controller state, and `dvz_camera_mvp()`.
* **Panel `DvzView3DDesc`**: semantically close to GSP, but it adds a second abstraction beside camera/controller APIs and bakes GSP’s first slice too high into Datoviz v0.4.
* **GSP adaptation with CPU/model transforms**: acceptable only as a non-strict fallback diagnostic path; it should not be used to claim strict View3D support.

## 3. **Python Binding Changes**

The ctypes generator should be upgraded, but with ABI validation as a hard gate. The current generator policy skips `vec*`, `dvec*`, `mat*`, and fixed float arrays, which is why `DvzCameraView`, `DvzCameraDesc`, and `DvzMVP` exist but are not safely usable from Python. 

Safe generator changes:

```python
vec2  -> ctypes.c_float * 2
vec3  -> ctypes.c_float * 3
vec4  -> layout-validated float[4], with required ABI alignment
dvec2 -> ctypes.c_double * 2
dvec3 -> ctypes.c_double * 3
dvec4 -> ctypes.c_double * 4
mat4  -> layout-validated 4x4 float storage, with required ABI alignment
```

Important qualification: `vec3` in the reported camera structs is straightforward because the ABI facts show size 36 / align 4 for `DvzCameraView`, with `eye`, `target`, and `up` at offsets 0, 12, and 24. `mat4` is **not** safe to blindly map as plain `(ctypes.c_float * 4) * 4` unless the generated ctypes type also matches the C ABI alignment. The reported `DvzMVP` ABI has size 208, alignment 16, and matrix offsets 0, 64, and 128; a naive ctypes nested float array will often have alignment 4 and produce the wrong aggregate alignment/size. 

Recommended binding policy:

* Add exact math-alias recognition before `_unsupported_field_layout()` rejects a record.
* Only treat exact aliases as known: `vec2`, `vec3`, `vec4`, `dvec2`, `dvec3`, `dvec4`, and `mat4`.
* Keep rejecting unknown `mat*`, unknown vector aliases, SIMD extension types, and arbitrary fixed numeric arrays until separately validated.
* Force layout emission for:

  * `DvzCameraView`
  * `DvzCameraProjection`
  * `DvzCameraDesc`
  * `DvzVisualAttachDesc`
* Force `DvzMVP` only if the generated Python type passes size, alignment, and offset tests. Otherwise keep `DvzMVP` opaque and do not advertise Python MVP inspection as supported.
* Remove `dvz_camera_view` and `dvz_camera_desc` from the skip list only after their return structs are layoutable.
* Add bindings for the new `dvz_camera_set_orthographic_bounds` symbol and probe it at runtime with `hasattr`/symbol lookup so older Datoviz builds remain cleanly unsupported.

For `mat4`, use a dedicated generated alias type rather than inlining plain arrays everywhere. A practical shape is a dedicated `DvzMat4` wrapper whose storage is 16 contiguous floats and whose alignment is ABI-validated. On platforms where ctypes cannot reproduce the required 16-byte alignment, the generator should fail the layout test and leave containing structs opaque instead of silently producing unsafe `_fields_`.

Required ABI tests:

```text
DvzCameraView:
  sizeof == 36
  alignof == 4
  eye offset == 0
  target offset == 12
  up offset == 24

DvzCameraProjection:
  sizeof == 20
  alignof == 4
  type offset == 0
  fov_y offset == 4
  near_clip offset == 8
  far_clip offset == 12
  ortho_height offset == 16

DvzCameraDesc:
  sizeof == 64
  alignof == 4
  struct_size offset == 0
  flags offset == 4
  view offset == 8
  projection offset == 44

DvzVisualAttachDesc:
  sizeof == 20
  alignof == 4
  struct_size offset == 0
  flags offset == 4
  z_layer offset == 8
  controller_mode offset == 12
  coord_space offset == 16

DvzMVP, only if exposed:
  sizeof == 208
  alignof == 16
  model offset == 0
  view offset == 64
  proj offset == 128
  time offset == 192
  flags offset == 196
```

Required smoke tests:

* `dvz_camera_view()` returns a Python object with writable `eye`, `target`, and `up`.
* `dvz_camera_desc()` returns a Python object whose `struct_size` equals `sizeof(DvzCameraDesc)`.
* `dvz_camera_set_view()` followed by `dvz_camera_get_view()` round-trips non-default `eye`, `target`, and `up`.
* `dvz_panel_set_camera(panel, &desc)` returns a usable `DvzCamera*`.
* `dvz_camera_set_orthographic_bounds()` can be called from Python with off-axis and reversed bounds.
* If `DvzMVP` is exposed, `dvz_camera_mvp()` writes matrices whose offsets and values match a C-side reference test.

## 4. **GSP Integration Contract**

After both the binding upgrade and the Datoviz orthographic-bounds API land, GSP may claim Datoviz support for:

```text
view3d.static.orthographic.v1
meshvisual.positions3d.data.view3d.v1
```

The claim should be conditional on a runtime/backend probe verifying all of the following:

* `dvz_camera_set_orthographic_bounds` is present.
* `DvzCameraView`, `DvzCameraDesc`, and `DvzVisualAttachDesc` ctypes layouts pass ABI validation.
* A panel camera can be created or retrieved.
* A Datoviz mesh visual can be attached in DATA coordinate space with `DVZ_CONTROLLER_APPLY_VIEW_PROJ`.
* Depth testing can be enabled through `dvz_visual_set_depth_test`.
* A runtime render probe verifies that `(N,3)` positions are actually transformed by camera view/projection and not treated as 2D data.

GSP lowering should be direct:

```text
Camera3D.eye      -> DvzCameraView.eye
Camera3D.target   -> DvzCameraView.target
Camera3D.up       -> DvzCameraView.up

OrthographicProjection3D.xlim[0]     -> left
OrthographicProjection3D.xlim[1]     -> right
OrthographicProjection3D.ylim[0]     -> bottom
OrthographicProjection3D.ylim[1]     -> top
OrthographicProjection3D.near_far[0] -> near_clip
OrthographicProjection3D.near_far[1] -> far_clip
```

GSP should continue to keep its own backend-neutral projection snapshots. It should not expose Datoviz matrices, `DvzMVP`, controller modes, Vulkan details, shader state, material structs, slot names, or Datoviz-specific camera descriptors through the public protocol.

Diagnostics that should remain:

```text
mesh3d_coordinate_space_unsupported
```

for older Datoviz builds without the required camera binding and bounds API.

A more specific diagnostic would also be useful:

```text
view3d_orthographic_bounds_unsupported:
Datoviz backend lacks public orthographic bounds camera support required for strict View3D
```

And this should still remain unavailable:

```text
query.view3d.ray_readback.v1
```

The prompt already marks Datoviz ray readback as deferred until render support exists, so this upgrade should not imply query support. 

## 5. **Tests**

Datoviz C camera tests:

* Centered compatibility: `dvz_camera_set_orthographic(height, near, far)` produces the same matrix as today.
* Bounds projection: `dvz_camera_set_orthographic_bounds(-2, 4, -1, 3, 0.1, 100)` makes `dvz_camera_mvp()` use those exact bounds.
* Off-axis projection: asymmetric bounds shift projected geometry as expected.
* Reversed x: `left > right` flips x deterministically; no normalization.
* Reversed y: `bottom > top` flips y deterministically; no normalization.
* Both reversed: matrix equals direct `glm_ortho(left, right, bottom, top, near, far)` behavior.
* Resize semantics: in bounds mode, `dvz_camera_resize()` does not rewrite explicit bounds; in centered mode, it still affects aspect-derived width.
* Mode reset: `dvz_camera_set_orthographic()` clears bounds mode; `dvz_camera_set_perspective()` clears bounds mode.
* Invalid bounds: equal x bounds, equal y bounds, equal near/far, NaN, and infinities are rejected or asserted consistently.

Datoviz Python ABI tests:

* Compare generated ctypes `sizeof`, `alignment`, and field offsets against generated C ABI facts for `DvzCameraView`, `DvzCameraProjection`, `DvzCameraDesc`, `DvzVisualAttachDesc`, and conditionally `DvzMVP`.
* Verify `dvz_camera_view()` and `dvz_camera_desc()` are emitted only when their by-value return layouts are valid.
* Round-trip `DvzCameraView` through `dvz_camera_set_view()` and `dvz_camera_get_view()`.
* Create or update a panel camera from Python and call `dvz_camera_set_orthographic_bounds()`.

Datoviz runtime rendering tests:

* Create an offscreen scene/panel, set a camera with explicit orthographic bounds, attach a mesh visual using DATA coordinates and `DVZ_CONTROLLER_APPLY_VIEW_PROJ`, then render.
* Projection test: render a simple square or triangle at known DATA coordinates and verify its pixel bounding box under symmetric bounds.
* Off-axis test: change only `left/right/bottom/top` to asymmetric bounds and verify the rendered object shifts as predicted.
* Reversed x/y tests: reversed `xlim` flips horizontally; reversed `ylim` flips vertically.
* Camera-view test: change `eye/target/up` while keeping mesh data constant and verify the image changes according to the view transform.
* Depth test: render two overlapping triangles or meshes with different z values and distinct colors; with depth test enabled, the nearer primitive must win regardless of draw order.
* Depth control: render the same case with depth test disabled or reversed draw order to prove the test is actually detecting depth behavior.
* Near/far clipping: place one primitive inside and one outside the clipping range and verify only the valid primitive contributes.
* Controller control: attach an otherwise identical visual in fixed/controller-bypassed mode and verify it does not respond to camera changes, while the DATA + view/proj visual does.

GSP probe/review tests:

* Capability probe is false for old Datoviz builds and true only when the new symbol and ABI layouts are valid.
* Strict parity tests against the Matplotlib reference path for:

  * centered unreversed bounds,
  * off-axis bounds,
  * reversed x bounds,
  * reversed y bounds,
  * both x and y reversed.
* Public snapshot tests confirm GSP exposes only `Camera3D`, `OrthographicProjection3D`, and `View3D`.
* API-surface tests confirm no Datoviz names, matrices, controller modes, Vulkan state, shader/material structs, or slot names leak into GSP public objects.
* Diagnostic tests confirm `query.view3d.ray_readback.v1` remains unavailable.

## 6. **Risks And Non-Goals**

Main risks:

* **ctypes alignment risk**: `mat4`/`DvzMVP` is the dangerous part. Do not expose `DvzMVP` as layoutable unless Python exactly matches the C ABI size, alignment, and offsets.
* **Clip-space convention risk**: Datoviz’s existing projection convention should remain the reference. The new API should feed explicit bounds into the same projection path rather than introducing a separate matrix convention.
* **Resize semantics risk**: explicit bounds and viewport aspect are different concepts. In bounds mode, resize changes the viewport, not the world-space bounds. That is correct for deterministic GSP snapshots but should be documented.
* **Reversed-bound rendering risk**: reversed x/y can interact with face winding or culling. This upgrade should not redesign culling; tests should either disable culling or document the existing Datoviz mesh behavior.
* **Partial-support risk**: supporting only centered orthographic through Datoviz and silently adapting off-axis/reversed cases would be misleading. Unsupported versions should keep diagnostics rather than claim strict support.

Rejected alternatives:

* **Binding-only**: rejected because it cannot represent GSP’s explicit ordered orthographic bounds.
* **Projection matrix API**: rejected because it is too low-level and makes resize/controller semantics ambiguous.
* **Panel `View3D` descriptor**: rejected for v0.4 because it duplicates the camera abstraction and risks becoming GSP-shaped API inside Datoviz.
* **CPU-transform/model-transform workaround**: rejected for strict support because it complicates deterministic parity, retained data semantics, and future ray/readback behavior.

Explicit non-goals:

* Perspective View3D.
* Interactive 3D navigation/controller API design.
* Ray casting, picking, readback, or `query.view3d.ray_readback.v1`.
* Full 3D scene graph design.
* Lighting, materials, normals, tangents, PBR, or shading policy.
* Mesh topology redesign beyond accepting/proving `(N,3)` DATA positions.
* Arbitrary user projection matrices.
* Vulkan state exposure.
* Public GSP exposure of Datoviz `DvzMVP`, controller modes, shader slots, material structs, or internal coordinate-space names.
* A general-purpose ctypes solution for every math/SIMD type in Datoviz; this upgrade should cover only the fixed aliases and structs needed for strict static orthographic View3D.
