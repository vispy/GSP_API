1. **Recommendation**

   S038 should accept **only `unlit_rgba` material semantics for existing `MeshVisual` RGBA colors**, with **no public `MeshMaterial3D` object, no normals, no lights, no textures, and no UVs**. This is the smallest correct public material model because it names what the protocol already supports: mesh color is a backend-neutral unlit surface color. S038 should be a spec/ADR plus capability/diagnostic/fixture update, not a new rendering-feature expansion. Lambert, Phong, texture sampling, generated normals, and reusable material/texture resources should remain deferred until their coordinate-space, color-space, alpha, sampler, and conformance rules are accepted.

2. **Accepted Public Concepts**

   * **Implicit mesh material kind: `unlit_rgba`**

     * Public capability label: `meshvisual.material.unlit_rgba.v1`.
     * This is a protocol concept, not a public object.
     * No new public field such as `MeshVisual.material` is required for S038.
     * A color-bearing `MeshVisual` without an explicit future material is interpreted as `unlit_rgba`.

   * **Existing `MeshVisual` RGBA color source becomes the base color source**

     * Bind the material semantics to the existing accepted color input, without widening it.
     * Conceptual type:

       ```python
       ColorSourceRGBA =
           RGBA                  # uniform color
         | Array[(N, 4), float]  # per-vertex color, only where already accepted
         | Array[(F, 4), float]  # per-face color, only where already accepted
       ```
     * `N` is vertex count.
     * `F` is face/triangle count.
     * The exact accepted color cardinalities remain governed by the existing `MeshVisual` color spec. S038 should not add new color cardinalities.

   * **Unlit color rule**

     * For strict opaque rendering:

       ```text
       output.rgb = base.rgb
       output.a   = base.a
       ```
     * No normal, light, camera position, view direction, depth value, or backend material state may modify the color.
     * Camera/projection affect geometry placement and depth only.

   * **Alpha rule**

     * Alpha is part of the RGBA color and is not multiplied by lighting.
     * Strict 3D mesh material conformance should only be claimed for opaque alpha, effectively `alpha == 1`.
     * Non-opaque alpha remains non-strict for 3D mesh composition and should continue to use `mesh3d_alpha_not_strict`.

   * **Color-space rule**

     * S038 should not define linear RGB, sRGB conversion, tone mapping, gamma correction, or physically meaningful lighting space.
     * For `unlit_rgba`, this is acceptable because there is no lighting math.
     * A backend claiming strict `unlit_rgba` must not apply implicit lighting or backend material tinting, but S038 should not claim full display color-management conformance.

   * **No public `View3D.lights`**

     * S038 should not add `View3D.lights`, `View3D.light_model`, ambient state, directional light state, or scene illumination containers.

   * **No public normals**

     * S038 should not add:

       ```python
       MeshVisual.normals
       MeshVisual.vertex_normals
       MeshVisual.face_normals
       ```
     * Backends must not generate normals as part of public protocol semantics.

   * **No public texture or UV fields**

     * S038 should not add:

       ```python
       Texture2D
       MeshVisual.uv
       MeshVisual.uvs
       MeshVisual.texture
       MeshVisual.sampler
       ```

3. **Deferred Concepts**

   * **`MeshMaterial3D` object**

     * Deferred because one accepted material kind does not justify a public object/resource model.
     * Adding the object now would create pressure to add backend-native material fields later.

   * **Normals**

     * Deferred because the protocol has not decided normal source, cardinality, coordinate space, normalization, degenerate-triangle behavior, winding interaction, or transform interaction.
     * Required before any Lambert or Phong material can be strict.

   * **Flat Lambert lighting**

     * Deferred. It is small conceptually but not yet small enough for this protocol because it requires accepted normal semantics, light-space semantics, color-combination semantics, color-space semantics, and deterministic backend fixtures.

   * **Ambient and directional lights**

     * Deferred. A future design should make ambient separate from directional illumination, but S038 should not add either.
     * A future directional light must explicitly define whether direction is in DATA/world, view/camera, or another named space.

   * **Phong/specular/shininess**

     * Deferred. Specular terms require view-vector semantics, normal interpolation rules, color-space rules, clamping rules, and backend shader parity.

   * **Textures, UVs, samplers, and unlit texture materials**

     * Deferred to a separate S039-style decision.
     * Texture support requires resource identity, lifetime, pixel format, color-space, UV cardinality, sampler wrap/filter rules, texture/color combination rules, and alpha rules.

   * **Generated normals**

     * Deferred. Backend-generated normals would make rendering dependent on triangulation, winding, duplicate vertices, smoothing policy, and backend implementation details.

   * **Transparency sorting**

     * Deferred. S038 should not expand beyond the existing opaque-depth baseline.

   * **Culling, shadows, PBR, model loading, instancing, scene graph**

     * Deferred as non-goals for this stage.

4. **Capability Names**

   | Capability string                        | Meaning                                                                       | Strict/adapted requirements                                                                                                                                                                                                                                                          | S038 disposition                                                                                       |
   | ---------------------------------------- | ----------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------ |
   | `meshvisual.material.unlit_rgba.v1`      | Existing `MeshVisual` RGBA colors are interpreted as an unlit mesh material.  | Strict: accepted RGBA color source is rendered without lighting, normals, texture sampling, view-dependent color change, or backend material tinting. Alpha is strict only for opaque meshes. Geometry/depth may still be governed by existing 3D mesh capabilities and diagnostics. | **Accept.**                                                                                            |
   | `meshvisual.material.flat_lambert.v1`    | Diffuse Lambert material using normals plus ambient/directional illumination. | Would require explicit normal source, normal space, light direction space, intensity/color rules, clamping, alpha behavior, and color-space fixtures.                                                                                                                                | **Defer.** Keep reserved only; do not advertise.                                                       |
   | `meshvisual.material.flat_phong.v1`      | Phong-like diffuse/specular material.                                         | Would require Lambert prerequisites plus view-vector semantics, specular color, shininess range, interpolation rules, and backend shader parity.                                                                                                                                     | **Defer.** Do not advertise.                                                                           |
   | `view3d.light.ambient.v1`                | Ambient illumination for 3D views.                                            | Would require a public lighting container and color/intensity/color-space rules. Should not exist independently before a material that consumes it.                                                                                                                                  | **Defer.**                                                                                             |
   | `view3d.light.directional.v1`            | Directional light for 3D views.                                               | Would require direction vector type, normalization, zero-vector rejection, coordinate-space rule, color/intensity rule, and deterministic Lambert fixtures.                                                                                                                          | **Defer.** Future ADR should either require a `space` field or rename to a space-qualified capability. |
   | `texture2d.rgba8.v1`                     | Public 2D RGBA8 texture resource.                                             | Requires resource ownership, shape, dtype, upload/update semantics, color-space, alpha, and backend lifetime rules.                                                                                                                                                                  | **Defer to S039 or later.**                                                                            |
   | `meshvisual.uv.vertex2d.v1`              | Per-vertex 2D UV coordinates for meshes.                                      | Requires UV cardinality, finite range policy, wrap/clamp behavior, interpolation, and interaction with indexed vertices.                                                                                                                                                             | **Defer to S039 or later.**                                                                            |
   | `meshvisual.material.texture2d_unlit.v1` | Unlit texture sampling on mesh surfaces.                                      | Requires `Texture2D`, UVs, sampler, texture/color combination, alpha, and color-space rules.                                                                                                                                                                                         | **Defer to S039 or later.**                                                                            |
   | `meshvisual.normals.vertex3d.v1`         | Per-vertex 3D normals.                                                        | Not currently reserved, but would require normal space, normalization, non-finite handling, zero-length handling, and interpolation rules.                                                                                                                                           | **Do not introduce in S038.**                                                                          |
   | `meshvisual.normals.face3d.v1`           | Per-face 3D normals.                                                          | Same as above, plus face-cardinality and flat-shading rules.                                                                                                                                                                                                                         | **Do not introduce in S038.**                                                                          |
   | `meshvisual.positions3d.opaque_depth.v1` | Existing opaque depth support for 3D mesh positions.                          | Unchanged. Material color and depth behavior remain separate. Matplotlib may remain adapted via sorting; Datoviz may be native depth-tested.                                                                                                                                         | **No S038 change.**                                                                                    |
   | `view3d.static.orthographic.v1`          | Existing static orthographic `View3D`.                                        | Unchanged. Required for `(N,3)` DATA mesh projection.                                                                                                                                                                                                                                | **No S038 change.**                                                                                    |

5. **Diagnostics**

   | Diagnostic code                       | Trigger                                                                                                                                                    | Recommended wording                                                                                                                         |
   | ------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
   | `mesh3d_material_unsupported`         | A public payload requests a material other than absent/implicit `unlit_rgba`, or a backend cannot support the requested material capability.               | `Mesh material '{material}' is not supported by this renderer/profile. S038 only accepts unlit RGBA mesh color semantics.`                  |
   | `mesh3d_material_object_unsupported`  | A payload or producer attempts to pass a public material object/resource such as `MeshMaterial3D`.                                                         | `Public mesh material objects are not part of S038. Use existing MeshVisual RGBA colors, interpreted as unlit_rgba.`                        |
   | `mesh3d_normals_unsupported`          | A payload includes normals in S038 public protocol.                                                                                                        | `Mesh normals are not part of the accepted S038 public protocol. Normals are reserved for a future material/light decision.`                |
   | `mesh3d_normals_missing`              | Future/experimental Lambert or Phong path is requested without required normals. Should not be emitted for accepted S038 `unlit_rgba`.                     | `The requested shaded mesh material requires explicit normals, but no accepted normal source was provided.`                                 |
   | `mesh3d_normals_nonfinite`            | Future/experimental normal payload contains NaN or infinite components. Public S038 validators may instead stop earlier with `mesh3d_normals_unsupported`. | `Mesh normals must be finite 3D vectors.`                                                                                                   |
   | `mesh3d_normals_invalid_zero`         | Future/experimental normal payload contains zero-length normals after validation. Not required for accepted S038.                                          | `Mesh normals must be non-zero vectors when used for shading.`                                                                              |
   | `view3d_light_unsupported`            | A payload includes public `View3D` light state or requests ambient/directional lighting in S038.                                                           | `View3D lights are not part of the accepted S038 public protocol. Lighting remains deferred.`                                               |
   | `view3d_light_invalid`                | Future/experimental light has non-finite color/intensity/direction, negative intensity, or invalid direction. Not required for accepted S038.              | `The requested View3D light has invalid parameters for the selected lighting model.`                                                        |
   | `texture2d_unsupported`               | A payload declares or references a public `Texture2D`.                                                                                                     | `Texture2D resources are not part of S038. Textured mesh materials remain deferred.`                                                        |
   | `mesh3d_uv_unsupported`               | A mesh payload includes UV coordinates.                                                                                                                    | `Mesh UV coordinates are not part of S038. UVs remain deferred with texture support.`                                                       |
   | `mesh3d_texture_material_unsupported` | A material requests texture sampling, texture/color combination, or a sampler.                                                                             | `Textured mesh materials are not part of S038. Use unlit RGBA colors only.`                                                                 |
   | `mesh3d_color_space_not_strict`       | A renderer or request tries to claim linear/sRGB/tone-mapped material semantics that S038 does not define.                                                 | `S038 does not define strict mesh material color-space conversion. Colors are unlit RGBA protocol values without lighting-space semantics.` |
   | `mesh3d_alpha_not_strict`             | Existing diagnostic: non-opaque 3D mesh alpha is requested where strict compositing is not supported.                                                      | `Non-opaque alpha for 3D mesh rendering is not strict in this renderer/profile.`                                                            |
   | `mesh3d_depth_adapted`                | Existing diagnostic: backend adapts opaque depth ordering, such as Matplotlib face sorting.                                                                | `3D mesh depth ordering is adapted by this renderer and may not provide native depth-buffer semantics.`                                     |

6. **Backend Semantics**

   **Matplotlib strict/adapted expectations**

   Matplotlib may claim `meshvisual.material.unlit_rgba.v1` only for the already accepted `MeshVisual` color modes it can preserve. It should render mesh colors without any public lighting, generated normals, texture sampling, Phong calculation, or backend material state. The material rule itself can be strict for opaque RGBA colors, while the existing 3D mesh rendering path remains adapted because vertices are CPU-projected to 2D collections and opaque depth is approximated by face sorting.

   Matplotlib legacy code for lighting, depth sorting variants, normals, Phong-like effects, and per-triangle texture warping must remain private/internal review technology. It must not cause Matplotlib to advertise Lambert, Phong, texture, UV, or light capabilities. If a public payload attempts to use those concepts, Matplotlib should issue the S038 diagnostics above instead of silently treating the legacy demo path as protocol support.

   **Datoviz strict/adapted expectations**

   Datoviz may claim `meshvisual.material.unlit_rgba.v1` if the GSP adapter can render retained mesh colors with implicit lighting disabled and without exposing Datoviz-native material structs, shader slots, Vulkan state, or camera/controller objects. Datoviz native depth testing can satisfy the existing opaque-depth path more directly than Matplotlib, but material conformance is still only about preserving unlit RGBA color semantics.

   Datoviz may have or later gain native material, lighting, normal, and texture capabilities, but those must remain behind the adapter until GSP accepts public protocol fields and conformance fixtures. No Datoviz-native material names should become public GSP API.

   **VisPy2 producer expectations**

   The VisPy2-style producer API should emit canonical `MeshVisual` objects with existing RGBA colors. It may provide ergonomic helpers that make unlit mesh color convenient, but it should not define public `MeshMaterial3D`, `PhongMaterial`, `LambertMaterial`, `Texture2D`, sampler, UV, or light semantics ahead of the accepted protocol. Producer helpers should validate or reject out-of-scope material/light/texture requests using the same diagnostics rather than inventing parallel semantics.

7. **Testing Plan**

   * **Capability advertisement fixture**

     * Renderer advertises `meshvisual.material.unlit_rgba.v1` only when it can preserve accepted `MeshVisual` RGBA color modes without implicit lighting or material tinting.

   * **Uniform unlit triangle**

     * One `(N,3)` DATA triangle in a `View3D` with uniform opaque RGBA.
     * Expected: projected geometry follows the canonical `View3D`; color is unchanged by camera orientation, depth, or absence/presence of any private backend light state.

   * **Per-face unlit mesh**

     * Two or more triangles with distinct per-face opaque colors.
     * Expected: each face keeps its assigned color; no lighting gradient appears.

   * **Per-vertex color fixture, only where already accepted**

     * If a renderer claims an accepted per-vertex color path, test that S038 does not reinterpret it as lighting or material interpolation beyond the existing color spec.
     * If Matplotlib adapts or cannot strictly interpolate per-vertex mesh color, it must not claim strict support for that color cardinality.

   * **Opaque depth interaction**

     * Overlapping opaque triangles with different depths and distinct colors.
     * Expected: material color remains unlit; depth behavior follows existing `meshvisual.positions3d.opaque_depth.v1` semantics.
     * Matplotlib may emit `mesh3d_depth_adapted`; Datoviz may use native depth testing.

   * **Alpha non-strict fixture**

     * Same mesh with `alpha < 1`.
     * Expected: material alpha is accepted as RGBA input, but strict 3D compositing is not claimed; emit or preserve `mesh3d_alpha_not_strict`.

   * **Negative material fixture**

     * Payload requests `material="flat_lambert"`, `material="flat_phong"`, a `MeshMaterial3D` object, or backend-native material state.
     * Expected: `mesh3d_material_unsupported` or `mesh3d_material_object_unsupported`.

   * **Negative normals fixture**

     * Payload includes vertex or face normals.
     * Expected: `mesh3d_normals_unsupported` for S038 public protocol.

   * **Negative light fixture**

     * Payload includes ambient or directional light state.
     * Expected: `view3d_light_unsupported`.

   * **Negative texture/UV fixture**

     * Payload includes `Texture2D`, UVs, sampler, or texture material.
     * Expected: `texture2d_unsupported`, `mesh3d_uv_unsupported`, or `mesh3d_texture_material_unsupported`.

   * **Snapshot/revision stability**

     * Adding S038 unlit material semantics must not perturb `View3DProjectionSnapshot` identity except where existing mesh visual payload serialization legitimately changes.
     * View/projection query payloads remain unaffected.

   * **Review examples**

     * Minimal colored cube or pyramid under orthographic `View3D`.
     * Overlapping opaque colored triangles showing depth behavior.
     * Explicitly labeled non-protocol internal demos, if kept, for Lambert/Phong/texture experiments.

8. **ADR/Spec Skeleton**

   * **ADR title**

     * `ADR-S038: MeshVisual Unlit RGBA Material Boundary`

   * **Spec filename**

     * `spec/visuals/mesh_materials_s038.md`

   * **Section outline**

     1. `Status`

        * Accepted, provisional, or ADR-only depending on fixture readiness.
     2. `Authority and Scope`

        * Reaffirm charter/spec authority order.
        * State that backend-native material/light/texture objects are not public API.
     3. `Problem`

        * Existing mesh colors need an explicit material interpretation before lighting/textures are added.
     4. `Decision`

        * S038 accepts only implicit `unlit_rgba`.
        * No public `MeshMaterial3D`, normals, lights, UVs, textures, or samplers.
     5. `Public Semantics`

        * Existing `MeshVisual` color source.
        * `output.rgb = base.rgb`.
        * `output.a = base.a`.
        * No light, normal, texture, camera, or view-dependent color term.
     6. `Alpha and Depth`

        * Opaque alpha is strict.
        * Non-opaque 3D mesh alpha remains non-strict.
        * Depth remains governed by existing 3D mesh depth capability and diagnostics.
     7. `Color-Space Boundary`

        * No linear/sRGB lighting space in S038.
        * No tone mapping or color-management claim.
     8. `Capabilities`

        * Accept `meshvisual.material.unlit_rgba.v1`.
        * Defer Lambert, Phong, ambient, directional, texture, UV capabilities.
     9. `Diagnostics`

        * Add material/light/normal/texture/UV rejection diagnostics.
        * Retain existing alpha/depth diagnostics.
     10. `Backend Conformance`

         * Matplotlib strict/adapted expectations.
         * Datoviz strict/adapted expectations.
         * VisPy2 producer expectations.
     11. `Fixtures`

         * Positive unlit RGBA fixtures.
         * Negative out-of-scope fixtures.
         * Snapshot stability checks.
     12. `Deferred Work`

         * Normals.
         * Lambert.
         * Phong/specular.
         * Textures/UVs/samplers.
         * Transparency sorting.
         * Culling/shadows/PBR/model loading.
     13. `Non-Goals and Private/Internal Code`

         * Legacy Matplotlib lighting/texture demos are not protocol support.
         * Datoviz-native material/light/shader state is not public API.

9. **Risks and Stop Conditions**

   S038 should remain ADR-only if the existing `MeshVisual` color rules are not yet precise enough to say which color cardinalities are strict, adapted, or unsupported. It should also remain ADR-only if either backend applies unavoidable implicit lighting/tinting, if unsupported material/light/normal/texture fields would be silently ignored, or if tests cannot distinguish material semantics from projection/depth behavior.

   Stop S038 from expanding if accepting Lambert would require adding normals, `View3D.lights`, color-space rules, or backend shader concepts in the same step. That would turn S038 from a boundary-setting material decision into a broad lighting system. The correct next step after S038 is a separate evidence-backed ADR for either Lambert-with-normals or unlit-texture-with-UVs, not both.

