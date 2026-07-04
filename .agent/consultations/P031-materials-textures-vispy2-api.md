# P031 - Materials, Textures, UVs, and VisPy2 3D API Shape

Date: 2026-07-04

Mission: M204 - S050 materials textures and VisPy2 API consultation planning

## Status

This needs ChatGPT Pro consultation.

Dependent implementation is paused until the user provides the consultation result.

## Prompt

Paste the following prompt into ChatGPT Pro:

```text
You are reviewing API/spec direction for GSP_API, a Python visualization protocol project with a
backend-neutral scene model and separate renderers/producers. Please answer as a senior graphics API
and scientific-visualization library architect.

Goal:
Decide the next safe protocol/API stage for mesh materials, textures/UVs, and high-level VisPy2
producer ergonomics after the accepted GSP milestones below. The output must be concrete enough to
drive ADR/spec writing and implementation missions, but must not propose implementation work that
violates the project's conservative capability-gated architecture.

Project authority and current facts:

1. Authority order is charter/spec/ADR over existing source. Existing code is implementation
   material, not authority.

2. GSP has an accepted `MeshVisual` protocol baseline:
   - `positions`: float `(N,2)` or `(N,3)`.
   - `faces`: integer `(M,3)` triangles only.
   - `coordinate_space`: `ndc` or `data`.
   - `color`: RGBA uniform `(4,)`, per-face `(M,4)`, or optional per-vertex `(N,4)`.
   - `color_mode`: `uniform`, `face`, or `vertex`.
   - `normal_mode`: `none`, `face`, `vertex`; only `face` is accepted for flat Lambert so far.
   - `normals`: optional face normals `(M,3)` for S039; vertex normals remain deferred.
   - `normal_generation`: `none` or `face_flat`.
   - `shading`: canonical `unlit_rgba` or `flat_lambert`; legacy `flat` may alias unlit, legacy
     `lambert` is not canonical.
   - `face_culling`: `none`, optional/capability-gated `back`/`front`.
   - `depth_test` / `depth_write`: `auto`, `disabled`, `enabled`.
   - `opacity_policy`: ordinary alpha only.
   - Public v1 explicitly excludes geometry resources, public material objects, lights beyond S039,
     textures, UVs, samplers, wireframe, mesh-local transforms, instances, scalar mesh colormaps,
     external model files, and backend draw calls.

3. Accepted View3D baseline:
   - `Camera3D` uses finite DATA-space `eye`, `target`, and `up`.
   - `OrthographicProjection3D` uses finite `xlim`, `ylim`, and `near_far`.
   - Panel NDC convention: x -1 left / +1 right, y -1 bottom / +1 top, z -1 near / +1 far, smaller z
     is closer.
   - Accepted capabilities include `view3d.static.orthographic.v1`,
     `meshvisual.positions3d.data.view3d.v1`, `meshvisual.positions3d.ndc.v1`,
     `meshvisual.positions3d.opaque_depth.v1`, `query.view3d.ray_readback.v1`, and after S044
     `query.view3d.mesh_triangle_pick.v1`.
   - Deferred concepts include matrix-first authoring, mesh-local 3D transforms, scene graphs,
     transparency sorting, strict clipping of partially clipped triangles, model loading,
     instancing, backend-native controllers, and non-mesh 3D visual families.

4. Accepted S038 material boundary:
   - The only S038 material concept is implicit `unlit_rgba`.
   - Existing `MeshVisual.color` is the final material color.
   - Strict `unlit_rgba`: `output.rgb = base.rgb`, `output.a = base.a`.
   - No normal, light, camera position, view direction, depth value, texture sample, generated
     backend attribute, or backend-native material state may modify the color.
   - Strict material conformance is opaque-only. Non-opaque 3D mesh alpha remains non-strict and
     should use `mesh3d_alpha_not_strict`.
   - Deferred/reserved capabilities include `meshvisual.material.flat_phong.v1`,
     `texture2d.rgba8.v1`, `meshvisual.uv.vertex2d.v1`, and
     `meshvisual.material.texture2d_unlit.v1`.
   - Unsupported material, light, normal, texture, or UV concepts must not be silently ignored when
     a public payload requests them.

5. Accepted S039 flat Lambert boundary:
   - Scope: flat Lambert diffuse shading only for opaque DATA-space 3D triangle meshes in a resolved
     `View3D`.
   - Accepted fields: `MeshVisual.shading="flat_lambert"`, `normal_mode="face"`, optional face
     `normals` `(F,3)`, `normal_generation="face_flat"`, `View3D.ambient_light_intensity`, and one
     optional scalar white DATA-space `DirectionalLight3D`.
   - Explicitly out of scope: public material objects, vertex normals, smooth Lambert, Phong,
     specular/shininess, textures, UVs, samplers, normal maps, multiple/colored/point/spot lights,
     attenuation, light IDs, scene graph, backend-native material/shader/draw-state objects.
   - Formula:
       n = normalize(face_normal)
       l = normalize(direction_to_light)
       D = directional_light.intensity * max(0, dot(n, l)) or 0 if no directional light
       L = clamp(ambient + D, 0, 1)
       output.rgb = clamp(base.rgb * L, 0, 1)
       output.a = base.a
   - Alpha is not lit. For alpha < 1, final 3D compositing remains non-strict.
   - Accepted capabilities: `meshvisual.material.flat_lambert.v1`,
     `meshvisual.normals.face3d.v1`, `meshvisual.normal_generation.face_flat.v1`,
     `view3d.light.ambient.v1`, `view3d.light.directional.v1`.
   - Prerequisites include `meshvisual.positions3d.opaque_depth.v1` for strict opaque ordering.

6. Current S050 state:
   - Datoviz mesh triangle picking remains blocked until upstream Datoviz exposes public canonical
     mesh face/triangle identity. Do not expand picking semantics based on private backend IDs.
   - S050 completed a strict opaque-depth promotion audit: Datoviz may advertise
     `meshvisual.positions3d.opaque_depth.v1` only for the retained DATA-space View3D path with fully
     opaque meshes and native depth test/write enabled.
   - Matplotlib 3D mesh raster remains adapted via CPU projection and face sorting, not strict
     fragment depth.
   - Non-opaque mesh alpha, culling, and expanded 3D query payloads are not accepted yet and have
     separate pending consultation needs.

7. VisPy2 current high-level producer API:
   - VisPy2 targets GSP, not Datoviz directly.
   - It currently offers ergonomic calls such as:
       fig, ax = vp.subplots()
       ax.set_xlim(...)
       ax.set_ylim(...)
       ax.imshow(...)
       ax.scatter(...)
       ax.markers(...)
       ax.path(...)
       ax.plot(...)
       ax.mesh(positions, faces, color=rgba, color_mode="face")
       fig.render_matplotlib()
       fig.savefig("out.png")
   - `Axes.mesh(positions, faces, color=..., color_mode=None, coordinate_space="data", order=0.0)`
     emits canonical `MeshVisual` for inline indexed triangles.
   - The current VisPy2 spec explicitly does not expose materials, lights, textures, normals,
     shading, culling, depth state, mesh-local transforms, Datoviz slots, or backend draw calls.
   - Public 3D camera/projection/navigation producer APIs remain deferred, although the lower-level
     GSP protocol has accepted View3D state and later navigation actions.

8. Important constraints:
   - Do not expose backend-native material structs, shader slots, Vulkan state, Matplotlib artists,
     Datoviz slots, camera/controller objects, or draw-call names as public GSP/VisPy2 API.
   - Do not make existing legacy material classes authoritative; they may inform design only.
   - Keep feature claims capability-gated and fixture-backed.
   - Prefer small separable stages. The S038 spec says the next material expansion should be either
     Lambert-with-normals or unlit-texture-with-UVs, not both in the same stage. S039 already handled
     flat Lambert face normals.
   - Avoid a broad scene graph or comprehensive 3D engine object model.

Questions to answer:

1. What should the next accepted stage be: unlit texture+UVs, vertex normals/smooth Lambert, Phong,
   culling/alpha, VisPy2 3D ergonomics, or something else? Choose one primary stage and explain why.

2. If the next stage is textures/UVs, define the minimal backend-neutral public protocol shape:
   resource model, accepted image dtype/shape, UV field shape/cardinality, coordinate convention,
   sampler/filter/wrap defaults, color multiplication rule, alpha rule, mipmap policy, color-space
   boundary, capability names, diagnostics, and fixture set.

3. If you recommend against textures/UVs next, define the smaller prerequisite stage instead with
   the same level of specificity.

4. What should VisPy2 expose in the next stage, if anything? Should it gain only thin producer
   conveniences that lower to accepted GSP protocol fields, or should it remain unchanged until the
   lower-level protocol lands? Provide exact method signatures only if you recommend adding them.

5. What should remain explicitly deferred after this stage? Include Phong/specular, smooth normals,
   vertex normals, multiple lights, alpha/transparency semantics, culling, model loading, instancing,
   mesh-local transforms, scene graph, and expanded query payloads.

6. What are the minimal conformance fixtures and negative tests required before any backend or
   producer capability is advertised?

Required output format:

Return exactly these sections:

1. Decision
   - One paragraph naming the recommended next stage and why.

2. Accepted Protocol Surface
   - A table of proposed public fields/resources/enums with types, defaults, and semantics.
   - If no new protocol fields should be added, say so explicitly and define the prerequisite work.

3. Capability Names And Diagnostics
   - A table of capability names.
   - A table of diagnostics.

4. Backend Conformance
   - Separate bullets for Matplotlib, Datoviz, and producer-only/VisPy2 behavior.

5. VisPy2 API
   - Exact recommended public method signatures or a statement that VisPy2 should not change yet.

6. Fixtures
   - Positive fixtures.
   - Negative fixtures.
   - Manual visual review artifacts if needed.

7. Deferred
   - A clear list of concepts that must remain out of scope.

8. Implementation Mission Plan
   - 5 to 8 bounded missions with acceptance criteria and stop conditions.

9. Risks / Open Questions
   - Any decisions that still need more evidence.
```

## Expected Result Handling

After the ChatGPT Pro result is pasted or committed:

1. Archive the response as `.agent/consultations/P031-response.md`.
2. Create an ADR/spec baseline for the accepted next stage only.
3. Do not implement materials, textures, UVs, smooth lighting, Phong, or broad VisPy2 helpers until
   the response is reviewed against existing specs.

