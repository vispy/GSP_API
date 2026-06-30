# P024 - S039 Lambert Normals Pre-Design

This needs ChatGPT Pro consultation.

## Prompt

You are reviewing an architecture/API decision for `GSP_API`, a Python visualization protocol/library
with Matplotlib and Datoviz v0.4 backends plus a VisPy2-style producer API. The goal is to decide
whether S039 should accept a minimal Lambert-with-normals material model after S038, and if yes, to
define the smallest correct public protocol surface.

Please answer as a protocol/API architect, not as code generation. The expected output format is at
the end.

### Project Authority and Constraints

Authority order in this repo is:

1. `PROJECT_CHARTER.md`
2. `ARCHITECTURE.md`
3. `SPEC_INDEX.md`
4. `spec/**`
5. accepted ADRs in `adr/**` and `.agent/decisions/**`
6. `LEGACY_MAP.md`
7. existing source code

Existing code is implementation material, not automatically authoritative. If legacy code conflicts
with accepted specs, specs win.

The public protocol is backend-neutral. It must not expose backend-native Datoviz material structs,
Vulkan/draw-state names, shader slots, controller objects, Matplotlib artists/axes, or legacy GSP
material classes as public API.

### Current Accepted State

S036/S037 define the bounded public 3D baseline:

- `Camera3D(eye, target, up)`.
- `OrthographicProjection3D(xlim, ylim, near_far)`.
- `View3D(id, panel_id, camera, projection, depth_mode=opaque_less, revision=...)`.
- Orthographic projection only.
- `MeshVisual.positions` accepts `(N,2)` and `(N,3)`.
- `(N,3)` plus `CoordinateSpace.DATA` projects through `View3D`.
- `(N,3)` plus `CoordinateSpace.NDC` is interpreted as panel NDC3 directly.
- Existing 2D affine transforms do not apply to `(N,3)` mesh geometry.
- `View3DProjectionSnapshot` provides deterministic projection snapshot IDs.
- `View3DQueryPayload` provides panel xy, panel NDC xy, near/far DATA points, ray direction, view id,
  view revision, layout snapshot id, and view/projection snapshot id.
- 3D mesh face picking remains deferred and returns `query_3d_visual_hit_deferred`.
- Public View3D navigation actions exist for orbit/pan/zoom/set/reset in the Matplotlib review path.
  Datoviz live View3D navigation remains deferred.

S038 accepted only implicit unlit RGBA mesh material semantics:

- `meshvisual.material.unlit_rgba.v1` is accepted.
- `unlit_rgba` is a protocol concept, not a public material object.
- Existing `MeshVisual.color` is the base color source.
- Strict opaque output is `output.rgb = base.rgb` and `output.a = base.a`.
- No normal, light, camera position, view direction, depth value, texture sample, generated backend
  attribute, or backend-native material state may modify the color.
- Non-opaque 3D mesh alpha remains non-strict and uses `mesh3d_alpha_not_strict`.
- S038 defines no strict linear RGB, sRGB conversion, tone mapping, gamma correction, or display
  color-management behavior.
- Public `MeshMaterial3D`, normals, generated normals, Lambert, Phong, lights, textures, UVs, and
  samplers remain deferred.

Accepted or reserved capability names currently include:

```text
view3d.static.orthographic.v1
meshvisual.positions3d.data.view3d.v1
meshvisual.positions3d.ndc.v1
meshvisual.positions3d.opaque_depth.v1
query.view3d.ray_readback.v1
view3d.navigation.orbit_pan_zoom.v1
meshvisual.material.unlit_rgba.v1
meshvisual.material.flat_lambert.v1   # reserved/deferred
meshvisual.material.flat_phong.v1     # reserved/deferred
view3d.light.ambient.v1               # reserved/deferred
view3d.light.directional.v1           # reserved/deferred
texture2d.rgba8.v1                    # reserved/deferred
meshvisual.uv.vertex2d.v1             # reserved/deferred
meshvisual.material.texture2d_unlit.v1 # reserved/deferred
```

### Current Implementation Reality

Public `MeshVisual` already has historical/optional fields in source code and S025-era docs:

- `normal_mode`: `none`, `face`, or `vertex`;
- `normals`: `(F,3)` or `(N,3)`;
- `normal_generation`: `none` or `face_flat`;
- `shading`: `flat` or historical optional `lambert`.

S038 explicitly states those fields are not accepted material semantics. They are historical optional
surface/implementation material until a later ADR accepts normal and lighting semantics.

Matplotlib:

- Reference for canonical View3D projection and ray-context payloads.
- 3D mesh rendering is adapted: 3D vertices are CPU-projected to 2D `PolyCollection` faces.
- Opaque depth is adapted by far-to-near face sorting for fixture triangles.
- Legacy/internal Matplotlib code exists for normal computation, depth sorting, simple lighting, and
  Phong-like or texture experiments. None of that is public protocol authority.

Datoviz v0.4:

- Can render static public `(N,3)` meshes through Datoviz panel camera state and explicit
  orthographic bounds on local builds with P022 camera bindings.
- Can advertise canonical `query.view3d.ray_readback.v1` payload generation from public View3D
  state.
- Supports retained mesh visuals and depth testing.
- May have or later gain native material/lighting/normal paths, but GSP must not expose
  Datoviz-native material names, shader slots, or Vulkan state.

VisPy2 producer API:

- Emits canonical protocol objects.
- Must not define engine/material semantics ahead of accepted protocol specs.

### Candidate S039 Scope

Candidate options:

1. **Defer Lambert again:** keep only `unlit_rgba` until backend evidence and normal semantics are
   stronger.
2. **Face-normal Lambert only:** accept per-face normals or deterministic face-normal generation for
   flat-shaded diffuse lighting.
3. **Vertex-normal Lambert:** accept per-vertex normals with interpolation rules, possibly alongside
   face normals.
4. **Minimal material/light objects:** add a narrow material kind plus one ambient term and one
   directional light.
5. **No material object:** keep material implicit and add only `shading="flat_lambert"` plus
   `View3D` light fields.

Do not include textures/UVs/samplers in S039. Do not include Phong/specular/shininess unless the
answer is to explicitly defer them.

### Questions To Answer

1. Should S039 accept Lambert-with-normals now, or defer it?
2. If accepted, should normals be face-only, vertex-only, both, or generated deterministically?
3. What should the exact public normal fields be, given the existing historical `MeshVisual` fields?
4. What coordinate space are normals in: DATA/world, model/local, view/camera, or something else?
5. How should normals be normalized, and how should zero, non-finite, or mismatched normals fail?
6. Should generated face normals be public protocol semantics? If yes, what is the winding and
   degeneracy policy?
7. Should S039 define a public material object, or a material/shading enum only?
8. What are the exact public fields for ambient and directional light, if accepted?
9. What coordinate space should directional light use?
10. Should ambient be a separate `View3D` light, a scalar on the material, or deferred?
11. What is the exact color-combination formula?
12. How should alpha behave?
13. Should shading math be specified in linear RGB, sRGB, or explicitly adapted/unspecified?
14. What capability names should be accepted, renamed, or kept reserved?
15. What diagnostics are required?
16. What does strict vs adapted support mean for Matplotlib and Datoviz?
17. What fixtures are required before any backend advertises support?
18. What must stay private/internal even if legacy code can demo it?

### Decision Constraints

- Keep public API minimal and backend-neutral.
- Avoid adding a scene graph.
- Avoid a broad material/resource system unless it is strictly necessary.
- Avoid backend-native material, shader, or draw-state names.
- Preserve deterministic testable semantics.
- Prefer one narrow capability-gated feature over a broad partial model.
- Explicitly distinguish strict support, adapted review support, and unsupported/deferred behavior.

## Expected Output Format

Please answer in this exact structure:

1. **Recommendation**
   - One paragraph naming the recommended S039 scope.

2. **Accepted Public Concepts**
   - Bullet list of concepts to add now, with exact field names and types where applicable.

3. **Deferred Concepts**
   - Bullet list of concepts to keep deferred, with short reasons.

4. **Normal Semantics**
   - Exact normal source, cardinality, coordinate-space, normalization, generation, winding, and
     invalid-input rules.

5. **Material and Light Semantics**
   - Exact material/light fields, color-combination formula, alpha rule, and color-space boundary.

6. **Capability Names**
   - Table with capability string, meaning, strict/adapted requirements, and disposition.

7. **Diagnostics**
   - Table with diagnostic code, trigger, and recommended wording.

8. **Backend Semantics**
   - Matplotlib strict/adapted expectations.
   - Datoviz strict/adapted expectations.
   - VisPy2 producer expectations.

9. **Testing Plan**
   - Positive and negative fixtures required before claiming support.

10. **ADR/Spec Skeleton**
   - ADR title, spec filename, and section outline.

11. **Risks and Stop Conditions**
   - Conditions under which S039 should remain ADR-only or defer Lambert.
