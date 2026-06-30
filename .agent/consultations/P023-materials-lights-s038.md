# P023 - S038 Materials, Lights, and Textures Pre-Design

This needs ChatGPT Pro consultation.

## Prompt

You are reviewing an architecture/API decision for `GSP_API`, a Python visualization protocol/library
with Matplotlib and Datoviz v0.4 backends plus a VisPy2-style producer API. The goal is to decide the
smallest correct public material/light model after the completed static View3D work.

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

The public protocol is intentionally backend-neutral. It must not expose backend-native Datoviz
camera objects, Vulkan/draw-state names, material structs, controller objects, shader slot names, or
Matplotlib artist objects as public GSP API.

### Current State After S037

S036/S037 now define and implement the bounded public 3D baseline:

- `Camera3D(eye, target, up)`.
- `OrthographicProjection3D(xlim, ylim, near_far)`.
- `View3D(id, panel_id, camera, projection, depth_mode=opaque_less, revision=...)`.
- Orthographic projection only.
- `MeshVisual.positions` accepts `(N,2)` and `(N,3)`.
- `(N,3)` + `CoordinateSpace.DATA` projects through `View3D`.
- `(N,3)` + `CoordinateSpace.NDC` is interpreted as panel NDC3 directly.
- Existing 2D affine transforms do not apply to `(N,3)` mesh geometry.
- `View3DProjectionSnapshot` provides deterministic projection snapshot IDs.
- `View3DQueryPayload` with payload kind `gsp.view3d-query@0.1` provides panel xy, panel NDC xy,
  near/far DATA points, ray direction, view id, view revision, layout snapshot id, and
  view/projection snapshot id.
- 3D mesh face picking remains deferred and returns `query_3d_visual_hit_deferred`.
- Public View3D navigation actions exist for orbit/pan/zoom/set/reset in the Matplotlib review path.
  Datoviz live View3D navigation remains deferred.

Accepted capability strings currently include:

```text
view3d.static.orthographic.v1
meshvisual.positions3d.data.view3d.v1
meshvisual.positions3d.ndc.v1
meshvisual.positions3d.opaque_depth.v1
query.view3d.ray_readback.v1
view3d.navigation.orbit_pan_zoom.v1
```

Accepted 3D diagnostics currently include:

```text
view3d_not_supported
view3d_projection_unsupported
view3d_invalid_camera_degenerate
view3d_invalid_projection
mesh3d_requires_view3d
mesh3d_coordinate_space_unsupported
mesh3d_transform_unsupported
mesh3d_depth_unsupported
mesh3d_depth_adapted
mesh3d_alpha_not_strict
mesh3d_clipping_adapted
query_3d_visual_hit_deferred
query_3d_snapshot_mismatch
view3d_navigation_unsupported
view3d_navigation_action_unsupported
view3d_navigation_snapshot_mismatch
view3d_navigation_invalid_delta
view3d_navigation_invalid_zoom
view3d_navigation_invalid_result
```

### Current Backend Reality

Matplotlib:

- Strict/reference for canonical View3D projection and ray-context payloads.
- Mesh rendering is adapted: 3D vertices are CPU-projected to 2D `PolyCollection` faces.
- Opaque depth is adapted by far-to-near face sorting for fixture triangles.
- Legacy/internal Matplotlib code exists for 3D techniques such as depth sorting, simple lighting,
  normals, and per-triangle texture warping, but none of that is public protocol authority.

Datoviz v0.4:

- After Datoviz P022 prerequisite commits, GSP can render static public `(N,3)` meshes through
  Datoviz panel camera state and explicit orthographic bounds.
- GSP can advertise `query.view3d.ray_readback.v1` for canonical ray-context payloads from public
  View3D state.
- Datoviz supports retained mesh visuals and depth testing.
- Datoviz has or is expected to grow native material/lighting/texture paths, but GSP must not expose
  Datoviz-native material names or Vulkan state directly.
- Datoviz guide/axis internals are being refactored separately and should not drive this decision.

VisPy2 producer API:

- May later expose ergonomic producer helpers that emit canonical protocol objects.
- Should not define public engine/material semantics ahead of the accepted protocol.

### Existing Reserved Future Names

S037 reserved, but did not claim, these future names:

```text
meshvisual.material.unlit_rgba.v1
meshvisual.material.flat_lambert.v1
meshvisual.material.flat_phong.v1
view3d.light.ambient.v1
view3d.light.directional.v1
texture2d.rgba8.v1
meshvisual.uv.vertex2d.v1
meshvisual.material.texture2d_unlit.v1
```

S037 wording says lighting or textured mesh support is strict only after public material, normal,
light-space, texture, UV, sampler, color-space, alpha, and color-combination rules are accepted and
evidence-backed. Legacy Matplotlib Phong or per-triangle affine texture output is experimental/adapted
until then.

### Current MeshVisual Baseline

Public `MeshVisual` is an inline indexed triangle mesh:

- finite positions, shape `(N,2)` or `(N,3)`;
- faces/triangles by index;
- colors may be uniform, per-vertex, or per-face RGBA depending on accepted renderer path;
- no public normals yet;
- no public UVs/textures yet;
- no public material object yet;
- no public culling/shadows/PBR/scene graph;
- no broad resource ownership model for reusable geometry/materials/textures in this stage.

S025/S036 intentionally deferred:

- normals;
- material models;
- lights;
- UVs/textures/samplers;
- culling;
- transparency sorting;
- arbitrary clipping semantics;
- 3D visual picking;
- OBJ/glTF/model loading;
- instancing;
- PBR/shadows.

### Candidate S038 Scope

We need to decide the smallest public S038 surface. Candidate options:

1. **Unlit only:** clarify that existing RGBA mesh color is an explicit unlit material and stop
   there for S038.
2. **Flat Lambert:** add optional per-face/per-vertex normals plus one directional light and ambient
   term, producing deterministic diffuse shading.
3. **Phong-like:** add diffuse/specular/shininess and stronger normal requirements.
4. **Texture proof:** add `Texture2D` + vertex UVs + unlit texture sampling.
5. **Defer implementation:** write ADR/spec only, with no new runtime support until backend evidence
   is stronger.

### Questions To Answer

1. Should S038 define a public `MeshMaterial3D` object, or should it first clarify existing RGBA
   colors as `unlit_rgba` without a material object?
2. Should S038 accept normals? If yes, should normals be per-vertex, per-face, generated by backend,
   or explicitly required?
3. Is flat Lambert directional lighting small and deterministic enough for S038, or should all
   lighting remain deferred?
4. If accepting Lambert, what are the exact public fields for material and lights?
5. Should ambient light be separate from directional light, or just a material/light scalar?
6. Should color combination be `base_rgba * light_intensity`, and how should alpha behave?
7. Should shading occur in linear RGB, sRGB, or explicitly unspecified/adapted for S038?
8. Should Phong/specular/shininess be deferred?
9. Should textures/UVs be part of S038, or explicitly separate S039?
10. What capability names should be accepted, renamed, or removed?
11. What diagnostics are required for missing normals, unsupported material, unsupported light,
    unsupported texture/UV, non-finite normals, and color-space limitations?
12. What does strict vs adapted support mean for Matplotlib and Datoviz?
13. What tests/fixtures are needed before claiming support?
14. What must stay private/internal even if legacy code can demo it?

### Decision Constraints

- Keep the public API minimal and backend-neutral.
- Avoid adding a scene graph.
- Avoid adding a general shader/material language.
- Avoid exposing backend-native material/light/texture objects.
- Preserve deterministic testable semantics.
- Prefer one or two capability-gated features over a broad partial model.
- Do not make textured/Phong demos appear as protocol support unless the protocol fields and tests
  are accepted.
- Explicitly distinguish strict support, adapted review support, and unsupported/deferred behavior.

## Expected Output Format

Please answer in this exact structure:

1. **Recommendation**
   - One paragraph naming the recommended S038 scope.

2. **Accepted Public Concepts**
   - Bullet list of concepts to add now, with exact field names and types where applicable.

3. **Deferred Concepts**
   - Bullet list of concepts to keep deferred, with short reasons.

4. **Capability Names**
   - Table with capability string, meaning, strict/adapted requirements, and whether to accept,
     rename, or defer.

5. **Diagnostics**
   - Table with diagnostic code, trigger, and recommended wording.

6. **Backend Semantics**
   - Matplotlib strict/adapted expectations.
   - Datoviz strict/adapted expectations.
   - VisPy2 producer expectations.

7. **Testing Plan**
   - Minimal conformance fixtures and review examples needed before claiming support.

8. **ADR/Spec Skeleton**
   - Proposed ADR title, spec filename, and section outline.

9. **Risks and Stop Conditions**
   - Conditions under which S038 should remain ADR-only.
