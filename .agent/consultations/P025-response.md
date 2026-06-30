1. **Recommendation**

   S040 should **promote Datoviz strict S039 flat Lambert only through CPU-resolved exact per-face colors**, not through native Datoviz lighting and not as a hybrid lighting path. The current `flat_lambert_unsupported` gate should remain until the CPU route is implemented and fixture-backed on the supported Datoviz v0.4 build matrix. This is strict because S039 defines the resolved material arithmetic and output RGBA, not a requirement that the backend run a live lighting engine. Datoviz’s public docs show that its mesh visual has lighting/material/color/normal controls, including vertex color, normals, diffuse/specular/emission parameters, and light direction-style controls, but that is not enough evidence that the native shader exactly matches S039’s DATA-space, face-normal, scalar-white ambient plus single directional Lambert formula. ([datoviz.org][1])

2. **Promotion Criteria**

   Datoviz may advertise strict S039 flat Lambert only when all of the following hold:

   * The Datoviz adapter calls the existing protocol validation path before upload:

     * `validate_mesh_visual_flat_lambert(visual, view3d=resolved_view3d)`;
     * canonical `MeshShading.FLAT_LAMBERT`;
     * resolved `View3D`;
     * DATA-space `(N,3)` triangle mesh;
     * `normal_mode="face"`;
     * explicit `(F,3)` normals with `normal_generation="none"`, or generated normals with `normal_generation="face_flat"`.
   * Face normals are resolved by protocol code before Datoviz upload:

     * explicit normals normalized by the protocol;
     * generated normals computed as `cross(p1 - p0, p2 - p0)` in DATA coordinates;
     * non-triangle, degenerate, zero-length, non-finite positions, non-finite normals, and non-finite lights fail before upload.
   * The adapter computes the S039 scalar lighting exactly in protocol/backend-neutral code:

     * `D = intensity * max(0, dot(normalize(n), normalize(direction_to_light)))`;
     * no directional term when no directional light exists;
     * `L = clamp(ambient + D, 0, 1)`;
     * `rgb = clamp(base.rgb * L, 0, 1)`;
     * `a = base.a`.
   * The Datoviz mesh upload uses the existing strict 3D DATA-space orthographic path and opaque depth path:

     * `view3d.static.orthographic.v1`;
     * `meshvisual.positions3d.data.view3d.v1`;
     * `meshvisual.positions3d.opaque_depth.v1`;
     * `meshvisual.material.unlit_rgba.v1`.
   * Datoviz native lighting, material diffuse/specular/emission parameters, normal generation, and shader-light controls are disabled, unused, or proven inert for this route.
   * Every rendered triangle receives a constant resolved color across the whole face. If Datoviz shades/interpolates vertex colors, the adapter must duplicate vertices per triangle and assign the same resolved RGBA to all three vertices.
   * Non-opaque 3D mesh alpha remains outside strict support and must continue to report `mesh3d_alpha_not_strict`.
   * Capability advertisement is fixture-backed:

     * CPU material arithmetic unit tests;
     * Datoviz adapter upload-shape tests;
     * rendered or readback comparison fixtures showing face-level constant colors;
     * negative validation tests showing invalid S039 inputs fail before Datoviz upload.
   * The capability snapshot is conservative: no `meshvisual.material.flat_lambert.v1` until all prerequisite capabilities are already present and passing for the same Datoviz path.

3. **Implementation Route**

   The Datoviz adapter should implement a **pre-upload protocol resolve stage**:

   1. Resolve `View3D` and run S039 validation.
   2. Resolve face normals using `MeshVisual.normalized_face_normals()` or the same protocol-normalization helper used by the reference path.
   3. Resolve one RGBA color per canonical face using the accepted S039 arithmetic.
   4. Convert the Lambert mesh into an unlit Datoviz mesh payload.
   5. Upload positions, indices, and color data through the existing C-shaped Datoviz v0.4 facade path.
   6. Keep depth testing enabled for opaque 3D meshes.
   7. Do not upload S039 normals for rendering purposes unless needed only for debug/probe instrumentation; the strict result should not depend on Datoviz normal interpretation.

   The safest upload shape is a **triangle-expanded mesh**:

   * Input:

     * positions: `(N,3)`;
     * faces: `(F,3)`;
     * resolved face colors: `(F,4)`.
   * Expanded upload:

     * positions: `(F * 3, 3)`, ordered as `p0, p1, p2` per face;
     * indices: either omitted if Datoviz supports non-indexed triangle upload, or set to `[[0,1,2], [3,4,5], ...]`;
     * colors: `(F * 3, 4)`, with each face color repeated three times.

   This avoids vertex-color interpolation changing face-level results. Even if Datoviz interpolates attributes across a triangle, interpolation among three identical RGBA values is constant. Datoviz’s Python docs describe mesh color as “color of the mesh vertices,” and expose normal, light, and material controls, which reinforces that strict S039 should not be inferred from native mesh lighting without probes. ([datoviz.org][2])

   A hybrid route should be rejected for S040. Using CPU-resolved colors while also enabling Datoviz lighting is not hybrid strict support; it is a double-lighting risk. A future native route may exist, but it must be separately proven and separately documented.

4. **Capability Advertisement**

   | Capability string                           | May Datoviz advertise under CPU-resolved S040? | Prerequisites                                                                                                                                                  |
   | ------------------------------------------- | ---------------------------------------------: | -------------------------------------------------------------------------------------------------------------------------------------------------------------- |
   | `view3d.static.orthographic.v1`             |                 Yes, if already fixture-backed | Resolved `View3D`; explicit orthographic bounds; DATA-space mapping proven on Datoviz v0.4 path                                                                |
   | `meshvisual.positions3d.data.view3d.v1`     |                 Yes, if already fixture-backed | Datoviz C-shaped facade mesh path renders `(N,3)` DATA-space positions in resolved `View3D`                                                                    |
   | `meshvisual.positions3d.opaque_depth.v1`    |                 Yes, if already fixture-backed | Datoviz depth testing enabled and positive/occlusion fixtures pass                                                                                             |
   | `meshvisual.material.unlit_rgba.v1`         |                                  Yes, required | Unlit RGBA upload path exists; native lighting disabled/unused; color fidelity fixture passes within accepted tolerance                                        |
   | `meshvisual.material.flat_lambert.v1`       |     Yes, only after CPU-resolved fixtures pass | All S039 arithmetic resolved before upload; triangle-expanded constant face colors; no native lighting contribution; alpha strictness limited to opaque meshes |
   | `meshvisual.normals.face3d.v1`              |        Yes, for protocol-resolved face normals | Explicit and generated face-normal validation pass; normals are DATA-space, finite, non-zero, normalized by protocol code                                      |
   | `meshvisual.normal_generation.face_flat.v1` |              Yes, for protocol generation only | Generated by protocol code using `cross(p1 - p0, p2 - p0)`; degenerate/non-finite/non-triangle failures tested                                                 |
   | `view3d.light.ambient.v1`                   |            Yes, as CPU-resolved material input | Scalar white ambient `[0,1]` validated and used only in CPU color resolve                                                                                      |
   | `view3d.light.directional.v1`               |            Yes, as CPU-resolved material input | Single directional light validated as finite non-zero DATA-space `direction_to_light`; scalar intensity `[0,1]`                                                |
   | Native Datoviz lighting/material capability |              No public S039 capability in S040 | Future-only; requires API probes and semantic equivalence evidence; must not expose native names                                                               |

5. **Diagnostics**

   | Diagnostic code                               | Trigger                                                                                                                             | Wording                                                                                                                                                                                          |
   | --------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
   | `flat_lambert_cpu_resolved_strict`            | Datoviz accepts S039 flat Lambert through the CPU-resolved route                                                                    | `flat_lambert_cpu_resolved_strict: Datoviz v0.4 S039 flat Lambert resolved by protocol CPU face colors; native Datoviz lighting is not used`                                                     |
   | `flat_lambert_native_lighting_unsupported`    | User/config/test attempts to route S039 through Datoviz native lighting, or capability probe asks whether native lighting is strict | `flat_lambert_native_lighting_unsupported: Datoviz native lighting/material semantics are not accepted as strict S039 evidence for this backend path`                                            |
   | `flat_lambert_unsupported`                    | S040 CPU route is not compiled, unavailable, not fixture-backed, or missing prerequisites                                           | `flat_lambert_unsupported: Datoviz v0.4 strict S039 flat Lambert support is not available because CPU-resolved face-color support or required View3D/depth prerequisites are not fixture-backed` |
   | `mesh3d_alpha_not_strict`                     | A Datoviz 3D mesh has non-opaque alpha under S039 or unlit RGBA strict path                                                         | `mesh3d_alpha_not_strict: Datoviz v0.4 3D mesh alpha is adapted/review-only; strict S039 support requires opaque mesh colors`                                                                    |
   | `flat_lambert_invalid_normal_input`           | Explicit normals contain zero-length, non-finite, wrong shape, or wrong mode/generation combination                                 | `flat_lambert_invalid_normal_input: S039 requires finite non-zero face normals or protocol-generated face_flat normals`                                                                          |
   | `flat_lambert_invalid_generated_normal`       | Generated face normal fails because of non-triangle, degenerate, or non-finite geometry                                             | `flat_lambert_invalid_generated_normal: S039 face_flat normal generation requires finite non-degenerate DATA-space triangles`                                                                    |
   | `flat_lambert_invalid_light`                  | Ambient or directional light violates scalar range or finite non-zero direction rules                                               | `flat_lambert_invalid_light: S039 requires ambient intensity in [0,1] and directional light intensity in [0,1] with finite non-zero DATA-space direction_to_light`                               |
   | `flat_lambert_upload_not_constant_face_color` | Adapter cannot guarantee each triangle receives a constant resolved RGBA                                                            | `flat_lambert_upload_not_constant_face_color: Datoviz upload would allow vertex-color interpolation to alter S039 face-level color; triangle-expanded constant colors are required`              |

6. **Fixtures**

   **Positive fixtures**

   * **Ambient-only face color**

     * One or more triangles, no directional light.
     * `ambient_light_intensity = 0`, `0.25`, `1`.
     * Verify `rgb = base.rgb * ambient`, alpha unchanged.
   * **Directional-only aligned normal**

     * `ambient = 0`;
     * normal parallel to `direction_to_light`;
     * `intensity = 1`;
     * verify full base RGB.
   * **Directional-only perpendicular normal**

     * dot product `0`;
     * verify black RGB when `ambient = 0`.
   * **Directional-only back-facing normal**

     * negative dot product;
     * verify directional term clamps to zero.
   * **Ambient plus directional clamp**

     * `ambient + D > 1`;
     * verify `L` clamps to `1`.
   * **Low-intensity scalar test**

     * non-trivial dot product, for example normalized vectors giving `D = 0.5 * intensity`;
     * verify scalar arithmetic, not binary lighting.
   * **Explicit normals path**

     * `(F,3)` normals with `normal_mode="face"` and `normal_generation="none"`;
     * verify protocol normalization and output colors.
   * **Generated normals path**

     * no normals, `normal_generation="face_flat"`;
     * verify generated normal orientation follows `cross(p1 - p0, p2 - p0)` in DATA coordinates.
   * **Per-face color discontinuity**

     * Two adjacent triangles sharing original vertices but producing different Lambert colors.
     * Verify the shared edge does not cause color averaging, smoothing, or interpolation across faces.
     * This is the key fixture proving vertex duplication.
   * **Indexed and expanded upload invariant**

     * Confirm the Datoviz upload uses `F * 3` vertices, or an equivalent no-interpolation representation.
     * Confirm all three uploaded vertices of each triangle have identical RGBA.
   * **Opaque depth compatibility**

     * Two overlapping opaque triangles/meshes with different depths.
     * Verify existing depth behavior remains strict after triangle expansion.
   * **Capability snapshot fixture**

     * When CPU route is enabled and all prerequisites pass, snapshot includes:

       * `meshvisual.material.flat_lambert.v1`;
       * `meshvisual.normals.face3d.v1`;
       * `meshvisual.normal_generation.face_flat.v1`;
       * `view3d.light.ambient.v1`;
       * `view3d.light.directional.v1`;
       * all prerequisite View3D/depth/unlit capabilities.
   * **Native-lighting-inert fixture**

     * Verify the CPU route does not call Datoviz native light/material controls for S039 rendering.
     * This can be an adapter mock/spy test, not necessarily an image test.

   **Negative fixtures**

   * **Unsupported until prerequisites**

     * Remove or disable any required View3D/depth/unlit fixture flag.
     * Verify `meshvisual.material.flat_lambert.v1` is not advertised.
   * **Non-triangle topology**

     * Faces not shaped `(F,3)` fail before upload.
   * **Degenerate triangle**

     * Repeated points or zero-area triangle under `face_flat` generation fails before upload.
   * **Non-finite positions**

     * `NaN`/`Inf` in positions fails before upload.
   * **Invalid explicit normals**

     * zero-length normals fail;
     * `NaN`/`Inf` normals fail;
     * wrong normal count fails;
     * wrong normal mode/generation combination fails.
   * **Invalid light**

     * ambient outside `[0,1]` fails;
     * directional intensity outside `[0,1]` fails;
     * zero-length or non-finite `direction_to_light` fails.
   * **No accidental native promotion**

     * A test that sees native Datoviz lighting APIs available must still not advertise strict native Lambert.
     * Official Datoviz docs mention mesh lighting and material controls, including diffuse/specular/emission and light controls, so the negative fixture should specifically prevent “API exists” from becoming “S039 strict.” ([datoviz.org][1])
   * **Alpha non-strict**

     * Any non-opaque 3D mesh alpha under Datoviz still reports `mesh3d_alpha_not_strict`.
     * It must not silently claim strict S039 alpha compositing.
   * **Shared-vertex interpolation failure detector**

     * A deliberately non-expanded upload of adjacent triangles with different face colors should fail the strict fixture or be tested at the adapter-shape level as prohibited.
   * **Color-management boundary**

     * Tests should assert only S039-defined arithmetic and accepted backend tolerance.
     * They should not introduce new linear RGB, sRGB, gamma, tone mapping, or display-management semantics.

7. **ADR/Spec Updates**

   A new ADR is appropriate because S040 is not merely an implementation detail; it changes the Datoviz backend’s advertised strict capability set and records a precedent that **CPU-resolved material semantics may satisfy a material capability when the accepted protocol defines output colors rather than a live shading engine**.

   Backend spec/docs updates are also required, but the accepted S039 public protocol spec should not be changed.

   Recommended updates:

   * New ADR, for example:

     * `adr/S040-datoviz-flat-lambert-cpu-resolve.md`, or the repo’s accepted ADR location.
     * Decision: Datoviz S039 flat Lambert strict support is CPU-resolved per-face color, not native lighting.
     * Consequences: triangle expansion, no native material exposure, no smooth/Phong/textures/multiple lights.
     * Stop conditions: keep unsupported if fixtures or prerequisites fail.
   * Datoviz backend spec section:

     * document strict CPU-resolved route;
     * document native lighting as out of scope for S040;
     * document alpha non-strict behavior.
   * Capability snapshot/generation docs:

     * add `meshvisual.material.flat_lambert.v1` only under the CPU route and only with prerequisite capabilities.
   * Diagnostics docs:

     * add/adjust diagnostic codes above.
   * `SPEC_INDEX.md`:

     * only update if it indexes backend-specific S040 documentation or ADR status.
   * `ARCHITECTURE.md`:

     * update only if it currently describes backend strictness categories or Datoviz capability advertisement rules.
   * Do **not** update public protocol semantics to add Datoviz material structs, native shader slots, material objects, vertex normals, smooth Lambert, Phong, textures, UVs, or multiple lights.

8. **Risks and Stop Conditions**

   Datoviz S039 Lambert should remain unsupported, and S040 should close with “keep unsupported” for release preparation, if any of these conditions hold:

   * The adapter cannot guarantee constant per-face color after Datoviz upload.
   * Datoviz requires shared vertex colors for the mesh path and cannot support triangle-expanded or equivalent per-face constant color upload.
   * The supported Datoviz v0.4 build matrix lacks stable `dvz_mesh`, `dvz_visual_set_data`, `dvz_visual_set_index_data`, or depth-test behavior needed by the strict path.
   * Existing View3D static orthographic DATA-space rendering is not fixture-backed on the release target.
   * Existing opaque depth support is not fixture-backed after the Lambert triangle-expansion path.
   * The CPU-resolved output cannot be compared deterministically within the project’s accepted rendering tolerance.
   * Non-opaque alpha cannot be cleanly diagnosed as `mesh3d_alpha_not_strict`.
   * The implementation would need to expose Datoviz-native material, lighting, shader, draw-state, or controller concepts through the public protocol.
   * The implementation would need to expand S039 semantics to vertex normals, smooth shading, Phong/specular/shininess, textures, UVs, samplers, multiple lights, colored lights, or a material resource system.
   * Tests can only prove Datoviz native lighting exists, not that it exactly matches S039. Datoviz documentation indicates mesh lighting/material APIs exist, but existence of those APIs is not semantic equivalence. ([datoviz.org][1])
   * Capability advertisement would be based on code intent rather than positive and negative fixtures.

   Final decision rule: **remove the current Datoviz gate only when CPU-resolved strict face-color fixtures pass and the capability snapshot is conservative; otherwise preserve `flat_lambert_unsupported` and proceed to release without Datoviz S039 Lambert promotion.**

[1]: https://datoviz.org/visuals/mesh/ "Mesh - Datoviz Documentation"
[2]: https://datoviz.org/reference/api_py/ "Python API Reference - Datoviz Documentation"

