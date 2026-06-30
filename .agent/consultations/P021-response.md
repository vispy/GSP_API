## 1. Executive Decision

* Treat S037 as **View3D navigation + Datoviz View3D binding**, not as a materials/lights/textures mission. The uploaded prompt establishes S036 as static, orthographic, backend-neutral, and intentionally without public material, light, UV, or texture semantics. 
* Reuse legacy Matplotlib **MVP projection, NDC conversion, view/world-space helper math, and face-depth sorting** immediately as internal implementation material only.
* Do **not** resurrect legacy public classes such as camera, material, light, Phong, depth, normal, or textured mesh APIs. Existing legacy code is useful implementation material, not authority.
* Keep Matplotlib 3D rendering explicitly **adapted**: CPU projection to 2D plus face sorting for opaque, non-intersecting triangles. Do not describe it as strict fragment-depth rendering.
* Fix Datoviz by adding a private `View3D` binding layer that lowers canonical GSP `Camera3D`, `OrthographicProjection3D`, `MeshVisual.positions`, coordinate space, colors, indices, and `depth_mode` into Datoviz. Do not expose Datoviz camera objects, draw-state names, or controller objects.
* Datoviz must continue returning `mesh3d_coordinate_space_unsupported` until there is backend evidence that `(N,3)` DATA and NDC meshes render through public GSP `View3D` semantics without silent z flattening.
* Add public navigation through backend-neutral **actions that produce new canonical `View3D` states**, not through backend-native controllers.
* Defer public lighting and texturing to later specs. Review-only Matplotlib demos are acceptable only if clearly marked non-public and not used as capability evidence.
* Add future material/light/texture capabilities only after public fields are accepted and both strictness and adaptation wording are nailed down.

## 2. Legacy Reuse Matrix

| Legacy technique                                                                          |                                              Reuse now? | Public API impact                                                                | Reason                                                                                                                                                                                                     | Tests needed                                                                                                                                  |
| ----------------------------------------------------------------------------------------- | ------------------------------------------------------: | -------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------- |
| MVP computation from model/view/projection matrices                                       |                                         Yes, internally | None                                                                             | Matches S036 need for deterministic projection from public `Camera3D` and `OrthographicProjection3D`. Use identity model for current `(N,3)` meshes unless a future public 3D model transform is accepted. | Matrix parity tests against S036 projection snapshots; degenerate camera/projection validation; deterministic `View3DProjectionSnapshot` IDs. |
| `MathUtils.apply_transform_matrix`-style homogeneous projection to NDC                    |                                         Yes, internally | None                                                                             | Directly supports DATA-to-panel-NDC projection and `(N,3)` NDC interpretation without exposing backend math APIs.                                                                                          | DATA positions project correctly; NDC3 bypasses view/projection; near/far DATA query points match snapshot math.                              |
| View-space vertices                                                                       |                                         Yes, internally | None                                                                             | Useful for depth ordering, clipping diagnostics, query consistency, and future lighting probes.                                                                                                            | View-space z/order tests; camera revision changes invalidate snapshots.                                                                       |
| World-space vertices                                                                      |                                  Limited internal reuse | None                                                                             | Useful for future lighting and diagnostics, but current S036 has no public 3D model transform. Keep identity/model-free for public behavior.                                                               | Identity-world parity tests; no acceptance of legacy model transform behavior.                                                                |
| Camera world-position extraction from inverse view matrix                                 |                                         Yes, internally | None                                                                             | Useful for ray readback and later lighting, derived from canonical `Camera3D`.                                                                                                                             | Ray direction and near/far query payload tests; degenerate camera rejection.                                                                  |
| NDC face-depth computation                                                                |                                                     Yes | None                                                                             | Already mirrored by S036 Matplotlib adapted face-order fixture. Keep for opaque, non-intersecting triangles.                                                                                               | Far-to-near sort fixture; order-independent triangle input; no claim for intersecting geometry.                                               |
| Far-to-near face sorting by average NDC z                                                 |                            Yes, Matplotlib adapted path | None                                                                             | Safe as an adapted painter-style approximation for opaque meshes; consistent with current Matplotlib behavior.                                                                                             | Opaque triangle ordering tests; translucent rejection via `mesh3d_alpha_not_strict`; fixture proving nearer faces draw last.                  |
| Screen-space face orientation / cross-z culling math                                      | Reuse as utility only; do not enable public culling yet | None now                                                                         | Backface culling changes visible output and S036 has no public culling field. Keep only for diagnostics or future spec work.                                                                               | Utility tests only; prove no default culling behavior change.                                                                                 |
| Face normal computation                                                                   |                                   Reuse as utility only | None now                                                                         | Needed for future flat lighting, normal debug, and review examples, but not part of current rendering contract.                                                                                            | Normal correctness tests on known triangles; zero-area handling; no public output changes.                                                    |
| Legacy flat Lambert + Phong lighting                                                      |                                                   Defer | Requires public material/light fields                                            | Needs accepted semantics for lights, normals, color combination, specular, shininess, coordinate space, and backend parity.                                                                                | Future lighting golden tests; strict/adapted renderer comparison; diagnostics for unsupported lights/materials.                               |
| Legacy depth material                                                                     |                                                   Defer | Requires public material/output-color semantics                                  | S036 depth is visibility/depth behavior, not a public color-mapped material.                                                                                                                               | Future material tests defining depth range, color mapping, clipping, and snapshots.                                                           |
| Legacy normal material                                                                    |                                                   Defer | Requires public material/output-color semantics                                  | Normal visualization is useful but must be specified as debug shading before being public.                                                                                                                 | Future tests defining normal space, normalization, handedness, and color encoding.                                                            |
| Legacy textured material using one Matplotlib `AxesImage` per triangle and affine UV warp |                                                   Defer | Requires public texture, UV, sampler, color-space, alpha, and material semantics | Too contract-heavy for S037. Can be preserved as a private review technique only.                                                                                                                          | Future UV interpolation tests; sampler tests; texture orientation tests; alpha/depth interaction tests; backend parity evidence.              |
| Legacy material class hierarchy                                                           |                                                      No | Would conflict with backend-neutral protocol                                     | Existing source code is not authoritative and legacy classes likely leak implementation concepts.                                                                                                          | None; migration tests should ensure no legacy material classes appear in public GSP API.                                                      |
| Legacy light objects                                                                      |                No for public API; utility concepts only | Would require new accepted protocol                                              | Directional/ambient/point-light semantics need explicit public fields and snapshots.                                                                                                                       | Future light-state serialization and renderer evidence.                                                                                       |
| Legacy camera object                                                                      |                                                      No | Conflicts with accepted `Camera3D`                                               | Public S036 camera is already `Camera3D(eye, target, up)`. Do not expose `src/gsp/core/camera.py` as authority.                                                                                            | API-surface test: only accepted public camera types exposed.                                                                                  |

## 3. Datoviz View3D Binding Plan

1. **Keep current refusal as the safe baseline.** Until the binding is proven, Datoviz v0.4 should continue rejecting public `(N,3)` meshes with `mesh3d_coordinate_space_unsupported` and a message explaining that public `View3D` camera binding is missing.

2. **Add a private `DatovizView3DAdapter`.** It should accept only public GSP state:

   * `View3D.id`
   * `View3D.panel_id`
   * `View3D.camera`
   * `View3D.projection`
   * `View3D.depth_mode`
   * `View3D.revision`
   * `MeshVisual.positions`
   * `MeshVisual` indices/faces
   * `MeshVisual` colors
   * `CoordinateSpace.DATA` or `CoordinateSpace.NDC`

3. **Derive all matrices from GSP state.** The adapter should compute the same canonical view, projection, view-projection, and projection snapshot identity used by S036. No Datoviz camera, controller, draw-state, or material object should appear in the public API.

4. **Implement DATA and NDC3 as separate lowering paths.**

   * `(N,3)` + `CoordinateSpace.DATA`: lower through the public `View3D` camera/projection semantics.
   * `(N,3)` + `CoordinateSpace.NDC`: bypass camera/projection and treat the coordinates as panel NDC3 directly.
   * `(N,2)` remains the existing bounded 2D mesh path.

5. **Do not silently flatten z.** A Datoviz path that uploads only xy or disables all meaningful depth behavior must not claim S036 3D mesh support.

6. **Bind depth privately.** For `depth_mode=opaque_less`, the adapter may privately enable Datoviz depth testing/writing only after evidence shows it implements the intended less-than opaque depth behavior. The public API still says `depth_mode=opaque_less`, not Datoviz depth-state names.

7. **Preserve existing 2D retained mesh behavior.** The current `dvz_mesh`, `position`, `color`, index-upload path for 2D should remain isolated from the new View3D adapter so bounded 2D behavior is not destabilized.

8. **Add an evidence-gated capability switch.** Datoviz should claim 3D capabilities only after tests pass. Before then, it should continue reporting unsupported diagnostics.

9. **Add screenshot or framebuffer fixtures only as evidence, not as protocol authority.** The protocol truth remains the public S036 state and deterministic CPU projection math.

10. **Add negative tests first.** Verify that Datoviz still rejects unsupported coordinate spaces, unsupported transforms on `(N,3)`, unsupported depth modes, translucent strict-depth cases, and missing `View3D`.

Required evidence before Datoviz can claim support:

| Evidence area         | Required proof                                                                                                                                                                                                   |
| --------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Public View3D binding | `Camera3D` and `OrthographicProjection3D` lower privately and match S036 CPU projection for known triangles.                                                                                                     |
| DATA positions        | `(N,3)` DATA mesh moves correctly when camera/projection changes.                                                                                                                                                |
| NDC positions         | `(N,3)` NDC mesh is interpreted directly as panel NDC3 and does not pass through the camera.                                                                                                                     |
| Depth                 | Opaque nearer triangles win regardless of index order, within the claimed strict/adapted mode.                                                                                                                   |
| Snapshot identity     | View/projection snapshot IDs change only when canonical View3D state changes.                                                                                                                                    |
| Query parity          | If claiming `query.view3d.ray_readback.v1`, payload fields match S036: panel xy, panel NDC xy, near/far DATA points, ray direction, view id, view revision, layout snapshot id, and view/projection snapshot id. |
| Diagnostics           | Missing binding still yields accepted diagnostics, not silent rendering.                                                                                                                                         |
| API hygiene           | No Datoviz camera, controller, draw-state, or material names appear in public GSP API.                                                                                                                           |

Diagnostics if unsupported:

| Condition                                                 | Diagnostic                                                                                                     |
| --------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------- |
| Backend has no public View3D binding path                 | `mesh3d_coordinate_space_unsupported` with the current Datoviz v0.4 explanation                                |
| `View3D` unavailable or not bindable                      | `view3d_not_supported`                                                                                         |
| Projection cannot be represented                          | `view3d_projection_unsupported`                                                                                |
| Invalid camera                                            | `view3d_invalid_camera_degenerate`                                                                             |
| Invalid projection                                        | `view3d_invalid_projection`                                                                                    |
| `(N,3)` mesh lacks a `View3D`                             | `mesh3d_requires_view3d`                                                                                       |
| Unsupported coordinate space                              | `mesh3d_coordinate_space_unsupported`                                                                          |
| 2D affine transform requested on `(N,3)` geometry         | `mesh3d_transform_unsupported`                                                                                 |
| Unsupported depth behavior                                | `mesh3d_depth_unsupported`                                                                                     |
| Depth is approximated/adapted                             | `mesh3d_depth_adapted`                                                                                         |
| Translucent 3D mesh requested in strict opaque-depth path | `mesh3d_alpha_not_strict`                                                                                      |
| Clipping is approximate/unverified                        | `mesh3d_clipping_adapted`                                                                                      |
| 3D face picking requested                                 | `query_3d_visual_hit_deferred`                                                                                 |
| Query/action uses stale snapshots                         | `query_3d_snapshot_mismatch`; for navigation, add `view3d_navigation_snapshot_mismatch` in the navigation spec |

## 4. Public View3D Navigation Contract

Expose navigation as **backend-neutral actions over canonical `View3D` state**. Do not expose Matplotlib callbacks, Datoviz controllers, trackball objects, camera handles, or backend-native event names.

Proposed public action objects:

```python
View3DNavigationAction(
    kind: Literal[
        "orbit",
        "pan",
        "zoom",
        "set_camera",
        "set_projection",
        "reset"
    ],
    view_id: str,
    base_view_revision: int,
    base_layout_snapshot_id: str | None,
    base_view_projection_snapshot_id: str,
    payload: OrbitPayload | PanPayload | ZoomPayload | SetCameraPayload | SetProjectionPayload | ResetPayload,
)
```

Payloads:

```python
OrbitPayload(
    delta_yaw_radians: float,
    delta_pitch_radians: float,
    pivot: Literal["target"] = "target",
    radius_policy: Literal["preserve"] = "preserve",
)
```

```python
PanPayload(
    delta_view_right: float,
    delta_view_up: float,
    units: Literal["data"] = "data",
)
```

```python
ZoomPayload(
    scale: float,
    anchor_panel_ndc_xy: tuple[float, float] | None = None,
)
```

```python
SetCameraPayload(
    camera: Camera3D,
)
```

```python
SetProjectionPayload(
    projection: OrthographicProjection3D,
)
```

```python
ResetPayload(
    camera: Camera3D,
    projection: OrthographicProjection3D,
)
```

Result event:

```python
View3DNavigationResult(
    view_id: str,
    old_revision: int,
    new_revision: int,
    camera: Camera3D,
    projection: OrthographicProjection3D,
    layout_snapshot_id: str | None,
    view_projection_snapshot_id: str,
    action_kind: str,
)
```

Revision and freshness rules:

| Rule                   | Contract                                                                                                                     |
| ---------------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| Canonical state        | `View3D.camera` and `View3D.projection` remain the source of truth.                                                          |
| Mutation model         | Navigation does not mutate backend camera objects directly; it produces a new canonical `View3D`.                            |
| Revision increment     | Any accepted camera/projection change increments `View3D.revision`.                                                          |
| Snapshot recomputation | Every accepted navigation result recomputes `View3DProjectionSnapshot`.                                                      |
| Stale action handling  | If `base_view_revision` or `base_view_projection_snapshot_id` does not match current state, reject the action.               |
| Layout freshness       | If an action uses `anchor_panel_ndc_xy` or panel-derived coordinates, `base_layout_snapshot_id` must match.                  |
| Query freshness        | Query payloads after navigation must carry the new view revision and view/projection snapshot id.                            |
| No implicit rebase     | Do not silently apply old actions to new camera state unless a later public `rebase=True` policy is specified.               |
| Degenerate result      | If orbit/pan/zoom creates invalid camera or projection state, reject and emit a diagnostic rather than normalizing silently. |

Navigation diagnostics to add in the navigation spec:

```text
view3d_navigation_unsupported
view3d_navigation_action_unsupported
view3d_navigation_snapshot_mismatch
view3d_navigation_invalid_delta
view3d_navigation_invalid_zoom
view3d_navigation_invalid_result
```

Backend-private items:

```text
Datoviz camera objects
Datoviz controller objects
Datoviz draw-state names
Matplotlib artist objects
Matplotlib axes objects
Matplotlib callback ids
Mouse-button bindings
Wheel-event scaling constants
Trackball implementation details
```

## 5. Materials Lights Textures

Defer public materials, lights, and textures from S037.

S037 should be:

```text
View3D navigation
Datoviz View3D binding
Matplotlib internal legacy-reuse cleanup
Capability wording and diagnostics hardening
```

It should not introduce:

```text
MeshBasicMaterial
MeshDepthMaterial
MeshNormalMaterial
MeshPhongMaterial
MeshTexturedMaterial
Light objects
Texture objects
UV attributes
Sampler state
Public culling flags
Public 3D model matrices
```

Review examples allowed meanwhile:

| Example type                              |                            Allowed? | Conditions                                                                                  |
| ----------------------------------------- | ----------------------------------: | ------------------------------------------------------------------------------------------- |
| Matplotlib private Phong demo             |                    Yes, review-only | Must be under an internal/experimental path and must not appear as public protocol support. |
| Matplotlib private textured-triangle demo |                    Yes, review-only | Must be labeled legacy technique exploration; no public capability claim.                   |
| Public lighting gallery example           |                                  No | Wait for accepted material/light spec.                                                      |
| Public textured mesh example              |                                  No | Wait for accepted texture/UV/sampler spec.                                                  |
| Datoviz 3D static mesh example            |    Yes, only after binding evidence | Must use only public `View3D` and `MeshVisual` fields.                                      |
| Datoviz navigation example                | Yes, only after navigation contract | Must emit canonical `View3DNavigationAction` and `View3DNavigationResult`.                  |

Future minimal model after S037 should be introduced in a separate spec, preferably S038, in this order:

1. **Unlit material clarification**, mostly documenting current color behavior.
2. **Flat Lambert directional lighting**, no specular yet.
3. **Flat Phong specular**, only after Lambert passes.
4. **Texture2D + vertex UVs**, after untextured lighting is stable.

Proposed future public fields, not for S037:

```python
MeshMaterial3D(
    kind: Literal["unlit", "flat_lambert", "flat_phong"],
    base_color: tuple[float, float, float, float] | None = None,
    color_source: Literal["visual_color", "material"] = "visual_color",
    alpha_mode: Literal["opaque"] = "opaque",
    normal_source: Literal["face"] = "face",
    shininess: float | None = None,
)
```

```python
AmbientLight3D(
    id: str,
    color: tuple[float, float, float] = (1.0, 1.0, 1.0),
    intensity: float = 0.0,
)
```

```python
DirectionalLight3D(
    id: str,
    direction: tuple[float, float, float],
    space: Literal["data", "view"] = "view",
    color: tuple[float, float, float] = (1.0, 1.0, 1.0),
    intensity: float = 1.0,
)
```

```python
Texture2D(
    id: str,
    width: int,
    height: int,
    format: Literal["rgba8"],
    color_space: Literal["srgb", "linear"] = "srgb",
)
```

```python
MeshTextureBinding(
    texture_id: str,
    uv: np.ndarray,  # shape (N, 2)
    sampler: TextureSampler2D,
    color_multiply: Literal["visual_color", "material", "none"] = "visual_color",
)
```

```python
TextureSampler2D(
    wrap_s: Literal["clamp", "repeat"] = "clamp",
    wrap_t: Literal["clamp", "repeat"] = "clamp",
    min_filter: Literal["nearest", "linear"] = "nearest",
    mag_filter: Literal["nearest", "linear"] = "nearest",
)
```

Future diagnostics:

```text
mesh3d_material_unsupported
mesh3d_lighting_unsupported
mesh3d_light_space_unsupported
mesh3d_normal_source_unsupported
mesh3d_texture_unsupported
mesh3d_uv_unsupported
mesh3d_sampler_unsupported
mesh3d_texture_alpha_unsupported
mesh3d_material_alpha_not_strict
```

## 6. Capability Wording

Existing S036 capability strings should remain semantic, not implementation-specific:

```text
view3d.static.orthographic.v1
meshvisual.positions3d.data.view3d.v1
meshvisual.positions3d.ndc.v1
meshvisual.positions3d.opaque_depth.v1
query.view3d.ray_readback.v1
```

Matplotlib projected mesh rendering:

```text
Matplotlib supports view3d.static.orthographic.v1 strictly for canonical Camera3D,
OrthographicProjection3D validation, deterministic projection snapshots, and
query ray readback.

Matplotlib supports meshvisual.positions3d.data.view3d.v1 in adapted rendering
mode: DATA-space (N,3) mesh positions are projected by the canonical S036 CPU
View3D math and rendered as 2D PolyCollection faces.

Matplotlib supports meshvisual.positions3d.ndc.v1 in adapted rendering mode:
NDC-space (N,3) mesh positions are interpreted as panel NDC3, then rendered
through the 2D Matplotlib collection path.

Matplotlib must not be described as a native retained 3D renderer for GSP View3D.
```

Matplotlib face sorting/depth:

```text
Matplotlib supports meshvisual.positions3d.opaque_depth.v1 only in adapted
opaque-depth mode: opaque, non-intersecting triangles are sorted far-to-near
by average panel-NDC z so nearer faces draw last.

This is not strict fragment-depth semantics. Translucent colors are rejected
from this path with mesh3d_alpha_not_strict. Partially clipped 3D triangles
remain adapted/unverified and may report mesh3d_clipping_adapted.
```

Datoviz retained 3D mesh rendering before evidence:

```text
Datoviz v0.4 does not claim view3d.static.orthographic.v1,
meshvisual.positions3d.data.view3d.v1, meshvisual.positions3d.ndc.v1,
meshvisual.positions3d.opaque_depth.v1, or query.view3d.ray_readback.v1 for
public (N,3) MeshVisual until public View3D binding evidence passes.

It must continue reporting mesh3d_coordinate_space_unsupported rather than
silently flattening z or exposing backend-native camera objects.
```

Datoviz retained 3D mesh rendering after evidence:

```text
Datoviz v0.4 supports view3d.static.orthographic.v1 strictly when public GSP
Camera3D and OrthographicProjection3D lower privately into Datoviz and match
canonical S036 projection snapshots.

Datoviz v0.4 supports meshvisual.positions3d.data.view3d.v1 strictly when
DATA-space (N,3) positions are retained as 3D geometry and transformed by the
public View3D state, not by backend-native public API.

Datoviz v0.4 supports meshvisual.positions3d.ndc.v1 strictly when NDC-space
(N,3) positions are interpreted directly as panel NDC3.

Datoviz v0.4 supports meshvisual.positions3d.opaque_depth.v1 strictly only
after evidence proves retained opaque less-depth behavior independent of
submission order.

Datoviz v0.4 supports query.view3d.ray_readback.v1 only if query payloads
match canonical S036 CPU snapshot semantics.
```

Navigation capability to add for S037:

```text
view3d.navigation.orbit_pan_zoom.v1
```

Wording:

```text
A backend supports view3d.navigation.orbit_pan_zoom.v1 when it accepts
backend-neutral View3DNavigationAction values for orbit, pan, zoom, reset,
set_camera, and set_projection; validates base revisions and snapshot IDs;
and returns a new canonical View3D state with a fresh revision and projection
snapshot. Native backend controller objects are not public API.
```

Future lighting capability names to reserve, not claim in S037:

```text
meshvisual.material.unlit_rgba.v1
meshvisual.material.flat_lambert.v1
meshvisual.material.flat_phong.v1
view3d.light.ambient.v1
view3d.light.directional.v1
```

Future lighting wording:

```text
Lighting support is strict only when public material, normal, light-space,
light-color, intensity, and color-combination rules are accepted and tested
against deterministic fixtures. Matplotlib-only legacy Phong output is
experimental/adapted until a public cross-backend contract exists.
```

Future texture capability names to reserve, not claim in S037:

```text
texture2d.rgba8.v1
meshvisual.uv.vertex2d.v1
meshvisual.material.texture2d_unlit.v1
texture2d.sampler.nearest_clamp.v1
texture2d.sampler.linear_clamp.v1
texture2d.sampler.nearest_repeat.v1
texture2d.sampler.linear_repeat.v1
```

Future texture wording:

```text
Textured mesh support is strict only when public Texture2D, UV attribute,
sampler, color-space, alpha, and color-multiply semantics are accepted and
both backends provide evidence. Legacy Matplotlib per-triangle affine texture
warping is not public support by itself.
```

## 7. Mission Plan

| Mission | Title                                  | Purpose                                                                                               | Deliverables                                                                                                                     | Stop condition                                                                                      |
| ------- | -------------------------------------- | ----------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------- |
| M161    | S036 3D Baseline Hardening             | Consolidate legacy-safe math into current S036 implementation without public API changes.             | Internal matrix/projection utility; NDC projection helper; face-depth helper; strict validation tests; no public legacy classes. | S036 tests pass; public API diff shows no material/light/texture/camera leakage.                    |
| M162    | Matplotlib Adapted Depth Contract Lock | Make Matplotlib adapted semantics explicit and test-backed.                                           | Far-to-near opaque face sorting tests; alpha rejection tests; clipping-adapted diagnostics; wording in backend capability docs.  | Matplotlib claims adapted opaque-depth only; no strict fragment-depth wording remains.              |
| M163    | S037 View3D Navigation Spec            | Define public navigation actions, result events, diagnostics, revision rules, and snapshot freshness. | `View3DNavigationAction`; payload dataclasses; `View3DNavigationResult`; diagnostics; pure reducer tests.                        | Navigation can be tested without Matplotlib or Datoviz.                                             |
| M164    | Matplotlib Navigation Adapter          | Wire public navigation actions to Matplotlib interaction without exposing Matplotlib objects.         | Orbit/pan/zoom handling; reset/set camera/projection; redraw on new `View3D`; query snapshot freshness tests.                    | Interactions produce canonical `View3D` revisions and fresh snapshots.                              |
| M165    | Datoviz View3D Evidence Spike          | Determine whether Datoviz v0.4 can privately bind public View3D semantics.                            | Runtime probes; minimal retained 3D triangle fixture; depth fixture; NDC3 fixture; evidence report.                              | Either evidence passes and implementation proceeds, or current unsupported diagnostics remain.      |
| M166    | Datoviz Static View3D Mesh Binding     | Implement the Datoviz 3D mesh path if M165 passes.                                                    | Private `DatovizView3DAdapter`; DATA and NDC3 lowering; colors/indices upload; depth-mode mapping; diagnostics.                  | Datoviz renders accepted `(N,3)` examples without z flattening and claims only proven capabilities. |
| M167    | Datoviz Query Ray Readback Parity      | Add or verify `query.view3d.ray_readback.v1` for Datoviz.                                             | Query payload generation from canonical snapshots; mismatch diagnostics; parity tests with Matplotlib CPU math.                  | Datoviz query payload fields match S036 semantics or capability remains unclaimed.                  |
| M168    | S037 Public Examples And Docs          | Publish only examples backed by accepted capabilities.                                                | Static View3D example; navigation example; Datoviz 3D example only if M166 passes; unsupported diagnostics example if not.       | No public lighting/texturing examples are presented as supported protocol.                          |
| M169    | S038 Materials/Lights ADR              | Decide the minimal public material/light model after S037.                                            | ADR/spec for `MeshMaterial3D`, ambient/directional lights, diagnostics, capability names, snapshots.                             | Accepted spec exists before implementation begins.                                                  |
| M170    | S039 Flat Lighting Implementation      | Implement the accepted minimal lighting model.                                                        | Matplotlib flat Lambert; Datoviz equivalent if available; fallback diagnostics; golden fixtures.                                 | At least one strict/adapted claim is evidence-backed and clearly worded.                            |
| M171    | S040 Texture/UV ADR And Prototype      | Define public texture semantics separately from lighting.                                             | `Texture2D`; UV attribute; sampler; color-space; alpha rules; review prototype.                                                  | No public textured capability is claimed until sampler/UV fixtures pass.                            |

## 8. Risks And Non-Goals

* Do not let legacy source files override accepted specs.
* Do not expose backend-native Datoviz camera objects, controller objects, draw-state names, or material structs.
* Do not expose Matplotlib artist or axes objects as GSP public API.
* Do not silently flatten z in Datoviz just to make `(N,3)` examples render.
* Do not describe Matplotlib face sorting as strict GPU-style fragment depth.
* Do not enable backface culling without an accepted public culling field.
* Do not add Phong, normal, depth, or textured materials by copying legacy class names into the public API.
* Do not add texture support without specifying UV orientation, sampler behavior, color space, alpha behavior, and color multiplication.
* Do not add lighting support without specifying normal space, light space, intensity units, color combination, and snapshot/revision behavior.
* Do not allow navigation actions to mutate backend state without producing a new canonical `View3D`.
* Do not accept stale navigation/query snapshots silently.
* Do not let public examples outrun public capability evidence.
* Do not claim Datoviz 3D support until retained 3D positions, camera/projection binding, NDC3 interpretation, and depth behavior are proven by tests.
