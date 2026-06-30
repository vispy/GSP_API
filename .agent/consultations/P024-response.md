1. **Recommendation**

   Accept S039, but only as a narrow, capability-gated **flat Lambert diffuse mode for opaque DATA-space 3D meshes using face normals**. S039 should not introduce `MeshMaterial3D`, vertex-normal interpolation, Phong/specular terms, texture inputs, backend-native material state, or a scene graph. The smallest correct public surface is: a canonical `MeshVisual.shading="flat_lambert"` selector, face-normal fields using the already existing historical `normal_mode`, `normals`, and `normal_generation` names, plus one scalar ambient term and at most one DATA-space directional light on `View3D`.

2. **Accepted Public Concepts**

   Add only these public protocol concepts:

   * `MeshVisual.shading: Literal["unlit_rgba", "flat_lambert"] = "unlit_rgba"`

     * `unlit_rgba` remains the S038 semantics.
     * `flat_lambert` is the only new S039 material/shading selector.
     * Legacy `shading="flat"` may remain as a compatibility alias for `unlit_rgba` in adapters, but it should not be the canonical protocol spelling.
     * Legacy `shading="lambert"` should not be canonical; it is too ambiguous.

   * `MeshVisual.normal_mode: Literal["none", "face"] = "none"`

     * `vertex` remains a legacy/deferred value and must not be accepted as S039 strict semantics.

   * `MeshVisual.normals: FloatArray[F, 3] | None = None`

     * Valid only when `normal_mode="face"`.
     * `F` is the canonical rendered face count for the mesh visual.

   * `MeshVisual.normal_generation: Literal["none", "face_flat"] = "none"`

     * `face_flat` means deterministic protocol generation of one face normal per canonical triangle face.
     * Generation is public S039 semantics only for DATA-space 3D triangle faces.

   * `View3D.ambient_light_intensity: float = 0.0`

     * Finite scalar in `[0.0, 1.0]`.
     * Applies only to `flat_lambert` meshes viewed through that `View3D`.

   * `View3D.directional_light: DirectionalLight3D | None = None`

   * `DirectionalLight3D.direction_to_light: tuple[float, float, float]`

     * Finite non-zero DATA-space vector.
     * Interpreted as the direction from the shaded surface point toward the light.

   * `DirectionalLight3D.intensity: float = 1.0`

     * Finite scalar in `[0.0, 1.0]`.

   No public material object should be added in S039. `flat_lambert` should be a material/shading enum value, not a `MeshMaterial3D` instance.

3. **Deferred Concepts**

   * `MeshMaterial3D`

     * Deferred because S039 needs only one material selector. A material object would prematurely imply a larger material/resource system.

   * Vertex normals, `normal_mode="vertex"`, and `normals.shape == (N, 3)`

     * Deferred because accepting them requires interpolation rules, face/vertex color interaction, normal transformation rules, and backend conformance fixtures.

   * Smooth Lambert shading

     * Deferred with vertex normals. S039 is flat Lambert only.

   * Phong, Blinn-Phong, specular color, shininess, view direction, camera position, and half-vector math

     * Deferred because they require additional material/light semantics and color-space decisions.

   * Multiple directional lights, point lights, spot lights, attenuation, light IDs, light lists, and scene light graphs

     * Deferred to avoid a scene graph or broad lighting resource model.

   * Light color

     * Deferred. S039 lights are scalar white-light terms only.

   * Textures, UVs, samplers, texture color multiplication, normal maps, generated backend attributes

     * Deferred by candidate scope and existing reserved capabilities.

   * Camera-space or view-space lights

     * Deferred. S039 uses DATA-space lighting only.

   * Lambert on `CoordinateSpace.NDC` meshes

     * Deferred because NDC3 meshes are panel-space geometry, not DATA/world-space geometry.

   * Non-triangular generated normals

     * Deferred unless an earlier mesh spec already defines canonical triangulation. S039 generation should be triangle-only for strict support.

   * Backend-native Datoviz material structs, Vulkan state, shader slots, Matplotlib artists/axes/controllers, and legacy GSP material classes

     * Must remain private implementation details.

4. **Normal Semantics**

   **Normal source**

   For `MeshVisual.shading="flat_lambert"`, exactly one of these normal sources is valid:

   * **Explicit face normals**

     * `normal_mode="face"`
     * `normals` is present
     * `normals.shape == (F, 3)`
     * `normal_generation="none"`

   * **Generated face normals**

     * `normal_mode="face"`
     * `normals is None`
     * `normal_generation="face_flat"`

   Any other combination is invalid for strict S039 Lambert.

   **Cardinality**

   * `F` is the canonical rendered face count of the mesh.
   * One normal applies to one face.
   * S039 does not define per-vertex normal cardinality.
   * S039 does not define normal interpolation.

   **Coordinate space**

   * Normals are in `CoordinateSpace.DATA`.
   * Generated normals are computed from `(N, 3)` DATA positions before View3D projection.
   * Explicit normals must already be expressed in the same DATA coordinate system as the mesh positions.
   * Existing 2D affine transforms do not apply to `(N, 3)` mesh geometry or normals.
   * There is no model/local normal space in S039 because S036/S037 have no public model transform or scene graph.
   * View/camera-space normals are deferred.
   * `flat_lambert` with `CoordinateSpace.NDC` positions is unsupported in S039.

   **Normalization**

   * Input normals do not need to be unit length.

   * The protocol normal used for shading is:

     ```text
     n = normal / length(normal)
     ```

   * Normalization is part of protocol semantics, not a backend convenience.

   * Negative components are valid.

   * Zero-length normals are invalid.

   * Non-finite components are invalid.

   * Normals whose computed length is non-finite are invalid.

   **Generated face normals**

   S039 should make generated face normals public protocol semantics, but only for canonical triangle faces.

   For a triangle face with DATA positions:

   ```text
   p0, p1, p2
   ```

   the generated raw normal is:

   ```text
   raw = cross(p1 - p0, p2 - p0)
   n = raw / length(raw)
   ```

   The winding is therefore right-handed with respect to the face vertex order. Reversing the face winding flips the generated normal. S039 must not auto-orient normals toward the camera, toward the light, or toward positive depth.

   **Degeneracy policy**

   * If `p0`, `p1`, or `p2` contains non-finite coordinates, generated normal validation fails.
   * If `cross(p1 - p0, p2 - p0)` is zero-length or non-finite, generated normal validation fails.
   * Degenerate faces must not silently receive `(0, 0, 1)`, previous-face normals, camera-facing normals, or backend-generated defaults.
   * Strict support should fail the visual or scene validation with a diagnostic rather than silently render a misleading Lambert result.

   **Invalid-input behavior**

   * `normal_mode="vertex"` is not S039 strict support.
   * `normals.shape == (N, 3)` is not S039 strict support.
   * `normal_mode="face"` with missing `normals` and `normal_generation="none"` is invalid for `flat_lambert`.
   * Explicit `normals` together with `normal_generation="face_flat"` is invalid; S039 should not define precedence.
   * `flat_lambert` on `(N, 2)` positions is invalid.
   * `flat_lambert` on `(N, 3)` NDC positions is invalid.

5. **Material and Light Semantics**

   **Material selector**

   S039 should not add a public material object. The only public material selector is:

   ```text
   MeshVisual.shading = "flat_lambert"
   ```

   `MeshVisual.color` remains the base color source, as in S038.

   **View3D lighting fields**

   ```python
   View3D.ambient_light_intensity: float = 0.0
   View3D.directional_light: DirectionalLight3D | None = None

   DirectionalLight3D.direction_to_light: tuple[float, float, float]
   DirectionalLight3D.intensity: float = 1.0
   ```

   Validation:

   * `ambient_light_intensity` must be finite and in `[0.0, 1.0]`.
   * If `directional_light is not None`, `direction_to_light` must be finite and non-zero.
   * `DirectionalLight3D.intensity` must be finite and in `[0.0, 1.0]`.
   * A missing directional light contributes `0.0` directional intensity.
   * A zero ambient term and no directional light is valid; the result is black RGB for Lambert meshes.

   **Directional light coordinate space**

   The directional light vector is in `CoordinateSpace.DATA`.

   It is interpreted as:

   ```text
   direction_to_light = direction from shaded point toward the light
   ```

   The Lambert term therefore uses:

   ```text
   max(0, dot(n, l))
   ```

   where `n` is the normalized face normal and `l` is the normalized `direction_to_light`.

   The light direction is not a camera direction, not a view-space vector, and not a backend-native light direction. View3D navigation changes projection, not the DATA-space light vector.

   **Color-combination formula**

   Let:

   ```text
   base = resolved S038 base RGBA from MeshVisual.color
   n    = normalized face normal in DATA space
   A    = View3D.ambient_light_intensity
   ```

   If `View3D.directional_light is None`:

   ```text
   D = 0
   ```

   Otherwise:

   ```text
   l = normalize(View3D.directional_light.direction_to_light)
   D = View3D.directional_light.intensity * max(0, dot(n, l))
   ```

   The scalar light factor is:

   ```text
   L = clamp(A + D, 0.0, 1.0)
   ```

   The output color is:

   ```text
   output.rgb = clamp(base.rgb * L, 0.0, 1.0)
   output.a   = base.a
   ```

   S039 lights are white scalar lights only. There is no light color, material diffuse color separate from `MeshVisual.color`, emissive term, specular term, texture term, depth term, camera-position term, or view-direction term.

   **Alpha rule**

   Alpha is not lit.

   ```text
   output.a = base.a
   ```

   For opaque meshes, strict S039 output can be tested with `base.a == 1.0`.

   For non-opaque 3D mesh alpha, S038’s non-strict rule remains:

   ```text
   mesh3d_alpha_not_strict
   ```

   S039 may define the pre-composition RGB and alpha values, but final blended appearance for alpha `< 1.0` remains adapted/non-strict.

   **Color-space boundary**

   S039 should not claim linear RGB, sRGB conversion, gamma correction, tone mapping, or display color-management semantics.

   The Lambert formula is defined over the normalized protocol color-channel values produced by S038 base color resolution. Strict tests should compare resolved protocol RGBA values or controlled backend readback, not unmanaged screenshots.

6. **Capability Names**

   | Capability string                           | Meaning                                       | Strict/adapted requirements                                                                                                                                                                                               | Disposition                             |
   | ------------------------------------------- | --------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------- |
   | `meshvisual.material.unlit_rgba.v1`         | S038 unlit base RGBA mesh color               | Strict opaque output remains `output.rgb = base.rgb`, `output.a = base.a`; normals/lights must not affect color                                                                                                           | Already accepted; unchanged             |
   | `meshvisual.material.flat_lambert.v1`       | S039 flat diffuse Lambert mesh shading        | Strict requires DATA-space `(N,3)` positions, View3D, face normals or deterministic generated face normals, exact scalar formula, and opaque conformance fixtures. Adapted support must be explicitly reported as adapted | Accept in S039                          |
   | `meshvisual.normals.face3d.v1`              | Explicit per-face 3D normals                  | Strict requires `normal_mode="face"`, `normals.shape == (F,3)`, finite non-zero normalization, and one normal per canonical rendered face                                                                                 | Add and accept in S039                  |
   | `meshvisual.normal_generation.face_flat.v1` | Deterministic generated triangle face normals | Strict requires canonical triangle faces, DATA-space positions, right-handed winding via `cross(p1-p0, p2-p0)`, and failure on degeneracy                                                                                 | Add and accept in S039                  |
   | `view3d.light.ambient.v1`                   | Scalar ambient term on `View3D`               | Strict requires finite `[0,1]` scalar and exact participation in `L = clamp(A + D, 0, 1)`                                                                                                                                 | Move from reserved/deferred to accepted |
   | `view3d.light.directional.v1`               | One DATA-space directional light on `View3D`  | Strict requires one optional directional light, finite non-zero DATA-space `direction_to_light`, finite `[0,1]` intensity, and exact dot-product semantics                                                                | Move from reserved/deferred to accepted |
   | `meshvisual.positions3d.data.view3d.v1`     | DATA-space 3D mesh projected through View3D   | Required prerequisite for strict S039 Lambert                                                                                                                                                                             | Already accepted; unchanged             |
   | `meshvisual.positions3d.ndc.v1`             | Panel NDC3 mesh coordinates                   | Remains accepted for unlit semantics, but not a strict S039 Lambert input                                                                                                                                                 | Already accepted; S039-incompatible     |
   | `meshvisual.positions3d.opaque_depth.v1`    | Opaque 3D mesh depth behavior                 | Required for strict opaque visual ordering; alpha still non-strict                                                                                                                                                        | Already accepted; unchanged             |
   | `view3d.static.orthographic.v1`             | Static orthographic View3D                    | Required View3D baseline for S039                                                                                                                                                                                         | Already accepted; unchanged             |
   | `query.view3d.ray_readback.v1`              | View3D ray-query payload                      | No S039 change                                                                                                                                                                                                            | Already accepted; unchanged             |
   | `view3d.navigation.orbit_pan_zoom.v1`       | Public View3D navigation actions              | No S039 change; lights are DATA-space and do not become camera-space during navigation                                                                                                                                    | Already accepted; unchanged             |
   | `meshvisual.normals.vertex3d.v1`            | Per-vertex normals                            | Would require interpolation and transform rules                                                                                                                                                                           | Keep reserved/deferred                  |
   | `meshvisual.material.smooth_lambert.v1`     | Smooth Lambert with vertex normals            | Not previously listed, but should remain unaccepted if named                                                                                                                                                              | Keep reserved/deferred                  |
   | `meshvisual.material.flat_phong.v1`         | Phong/specular material                       | Requires view direction, specular color, shininess, and color-space decisions                                                                                                                                             | Keep reserved/deferred                  |
   | `texture2d.rgba8.v1`                        | 2D texture resource                           | Out of S039 scope                                                                                                                                                                                                         | Keep reserved/deferred                  |
   | `meshvisual.uv.vertex2d.v1`                 | Per-vertex UVs                                | Out of S039 scope                                                                                                                                                                                                         | Keep reserved/deferred                  |
   | `meshvisual.material.texture2d_unlit.v1`    | Unlit textured material                       | Out of S039 scope                                                                                                                                                                                                         | Keep reserved/deferred                  |

7. **Diagnostics**

   | Diagnostic code                                 | Trigger                                                                                              | Recommended wording                                                                              |
   | ----------------------------------------------- | ---------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------ |
   | `flat_lambert_requires_view3d`                  | `shading="flat_lambert"` used without a resolved `View3D`                                            | `flat_lambert shading requires a resolved View3D.`                                               |
   | `flat_lambert_requires_data3d_positions`        | Lambert mesh positions are not `(N,3)` DATA coordinates                                              | `flat_lambert requires MeshVisual.positions with shape (N,3) in CoordinateSpace.DATA.`           |
   | `flat_lambert_requires_face_normals`            | Lambert mesh has neither explicit face normals nor `normal_generation="face_flat"`                   | `flat_lambert requires face normals or deterministic face_flat normal generation.`               |
   | `vertex_normals_deferred`                       | `normal_mode="vertex"` or `(N,3)` normals are used for S039 Lambert                                  | `Vertex normals and smooth Lambert shading are deferred; S039 accepts face normals only.`        |
   | `normal_source_conflict`                        | Both explicit `normals` and `normal_generation="face_flat"` are supplied                             | `Specify either explicit face normals or face_flat normal generation, not both.`                 |
   | `normal_mode_normals_conflict`                  | `normal_mode="none"` with `normals` present, or `normal_mode="face"` with incompatible normal fields | `MeshVisual normal fields are inconsistent with normal_mode.`                                    |
   | `face_normals_shape_mismatch`                   | Explicit normals are not shaped `(F,3)`                                                              | `Face normals must have shape (F,3), where F is the canonical rendered face count.`              |
   | `normal_nonfinite`                              | Explicit normal contains NaN or infinity                                                             | `Face normals must contain only finite numeric values.`                                          |
   | `normal_zero_length`                            | Explicit normal has zero length                                                                      | `Face normals must be non-zero so they can be normalized.`                                       |
   | `face_normal_generation_nontriangular_deferred` | `normal_generation="face_flat"` requested for non-triangle canonical faces                           | `S039 face_flat normal generation is defined only for canonical triangle faces.`                 |
   | `face_normal_generation_degenerate`             | Generated triangle normal has zero or non-finite length                                              | `Cannot generate a face normal for a degenerate or non-finite triangle.`                         |
   | `ambient_light_invalid`                         | Ambient intensity is non-finite or outside `[0,1]`                                                   | `View3D ambient_light_intensity must be finite and within [0,1].`                                |
   | `directional_light_direction_invalid`           | Directional light vector is missing, non-finite, or zero-length                                      | `DirectionalLight3D.direction_to_light must be a finite non-zero DATA-space vector.`             |
   | `directional_light_intensity_invalid`           | Directional light intensity is non-finite or outside `[0,1]`                                         | `DirectionalLight3D.intensity must be finite and within [0,1].`                                  |
   | `legacy_lambert_shading_not_canonical`          | Legacy `shading="lambert"` appears in public protocol input                                          | `Use canonical shading="flat_lambert"; legacy shading="lambert" is not S039 protocol semantics.` |
   | `flat_lambert_unsupported`                      | Backend lacks S039 support and cannot provide an adapted fallback                                    | `Backend does not support meshvisual.material.flat_lambert.v1 for this visual.`                  |
   | `flat_lambert_adapted_not_strict`               | Backend renders approximate/review Lambert only                                                      | `flat_lambert is rendered in adapted review mode; strict color conformance is not claimed.`      |
   | `mesh3d_alpha_not_strict`                       | Lambert mesh has alpha `< 1.0`                                                                       | `Non-opaque 3D mesh alpha remains non-strict; RGB is defined before backend compositing only.`   |

8. **Backend Semantics**

   **Matplotlib strict/adapted expectations**

   Matplotlib should be treated primarily as an **adapted review backend** for S039 visual rendering.

   It may compute S039 face normals and Lambert face colors on the CPU from canonical protocol fields, then pass resolved per-face colors to its existing `PolyCollection` path. That can be a strict implementation of the **material math** if fixtures compare the resolved face RGBA values before Matplotlib-specific rendering.

   However, Matplotlib should not claim fully strict visual rendering for the whole 3D mesh pipeline unless the repo has explicit fixtures proving the combined projection, face sorting, color assignment, and opaque depth behavior under the accepted tolerances. Its 3D rendering remains adapted because vertices are CPU-projected to 2D collections and depth is represented by far-to-near face sorting.

   Matplotlib must not expose public artists, axes, collections, controller objects, private depth-sort knobs, or legacy material classes as S039 API.

   **Datoviz strict/adapted expectations**

   Datoviz may claim strict S039 support only if it implements the exact GSP protocol semantics, not merely a visually similar Datoviz-native material.

   Strict Datoviz support can be achieved by either:

   * a GSP-controlled Datoviz path that supplies face normals and implements the exact S039 formula; or
   * CPU-resolving flat Lambert face colors according to S039 and submitting those colors through an unlit retained mesh path, provided the rendered primitive topology preserves one color per face.

   Datoviz must not expose native material structs, shader slots, Vulkan state names, draw-state names, or backend-native lighting names as public GSP protocol.

   If Datoviz uses a native Lambert/material path whose normal interpolation, color space, light direction convention, gamma behavior, or alpha behavior differs from S039, it may at most advertise adapted review support with `flat_lambert_adapted_not_strict`.

   Datoviz live View3D navigation remains outside S039. Because S039 lights are DATA-space, navigation should not silently convert lights into camera-space headlights.

   **VisPy2 producer expectations**

   The VisPy2-style producer API should emit only canonical protocol fields:

   ```text
   shading="flat_lambert"
   normal_mode="face"
   normals=(F,3) or normal_generation="face_flat"
   View3D.ambient_light_intensity
   View3D.directional_light
   ```

   It must not define engine-specific material semantics ahead of the accepted protocol. It should validate or pass through diagnostics for unsupported vertex normals, legacy `shading="lambert"`, texture fields, Phong fields, backend-native materials, and NDC Lambert attempts.

   A producer may offer convenience helpers, but the emitted protocol snapshot must contain the canonical S039 fields and capability names.

9. **Testing Plan**

   Required positive fixtures before any backend advertises S039 support:

   * **Explicit face-normal fixture**

     * One triangle with `normal_mode="face"` and `normals.shape == (1,3)`.
     * Directional light aligned with the normal.
     * Expected `L = ambient + directional`.

   * **Normal normalization fixture**

     * Same triangle rendered with normal `(0,0,1)` and `(0,0,10)`.
     * Expected identical output RGB.

   * **Back-facing clamp fixture**

     * Normal opposite the light direction.
     * Expected directional term `0`, ambient only.

   * **Generated normal fixture**

     * Triangle in DATA XY plane with CCW winding.
     * `normal_generation="face_flat"`.
     * Expected generated normal `+Z`.

   * **Reversed winding fixture**

     * Same triangle with reversed indices.
     * Expected generated normal `-Z` and different Lambert result.

   * **Ambient-only fixture**

     * `directional_light=None`, non-zero ambient.
     * Expected `output.rgb = base.rgb * ambient`.

   * **Directional-only fixture**

     * `ambient_light_intensity=0`.
     * Expected pure Lambert dot product.

   * **Clamp fixture**

     * Ambient plus directional sum greater than `1`.
     * Expected `L = 1`.

   * **Per-face fixture**

     * Two triangles with different normals and same base color.
     * Expected different face colors and no normal interpolation.

   * **Camera/navigation invariance fixture**

     * Same DATA mesh and same DATA-space light rendered through different camera positions.
     * Expected same per-face Lambert RGB before raster/display effects.

   * **Alpha passthrough fixture**

     * Base alpha `1.0` and base alpha `<1.0`.
     * Expected `output.a = base.a`; alpha `<1.0` emits or preserves `mesh3d_alpha_not_strict`.

   * **Capability fixture**

     * Backend advertises `meshvisual.material.flat_lambert.v1` only when it also satisfies required face normal and View3D light semantics.

   Required negative fixtures:

   * `shading="flat_lambert"` with `(N,2)` positions.
   * `shading="flat_lambert"` with `(N,3)` `CoordinateSpace.NDC` positions.
   * `shading="flat_lambert"` without `View3D`.
   * `normal_mode="vertex"` with Lambert.
   * `normals.shape == (N,3)` with Lambert.
   * Explicit normals shaped other than `(F,3)`.
   * Explicit normals containing NaN or infinity.
   * Explicit zero-length normal.
   * Both explicit normals and `normal_generation="face_flat"`.
   * `normal_generation="face_flat"` on degenerate triangle.
   * `normal_generation="face_flat"` on non-triangle canonical face, unless another accepted mesh spec has already defined canonical triangulation.
   * Directional light with zero vector.
   * Directional light with NaN or infinity.
   * Ambient or directional intensity outside `[0,1]`.
   * Legacy `shading="lambert"` in canonical protocol input.
   * Phong/specular/texture/UV fields attempting to affect Lambert color.
   * Backend-native Datoviz material names or shader slots appearing in public protocol snapshots.

10. **ADR/Spec Skeleton**

**ADR title**

```text
ADR S039: Minimal Flat Lambert Mesh Shading with Face Normals
```

**Spec filename**

```text
spec/S039_meshvisual_flat_lambert_normals.md
```

**Section outline**

1. Status and authority

   * Accepted after S038.
   * S039 extends S038 only for flat Lambert opaque DATA-space 3D meshes.

2. Scope

   * In scope: face normals, deterministic triangle face-normal generation, scalar ambient, one DATA-space directional light, exact RGB formula.
   * Out of scope: material objects, vertex normals, Phong, textures, UVs, samplers, light colors, multiple lights, scene graph, backend-native materials.

3. Public schema additions

   * `MeshVisual.shading`
   * `MeshVisual.normal_mode`
   * `MeshVisual.normals`
   * `MeshVisual.normal_generation`
   * `View3D.ambient_light_intensity`
   * `View3D.directional_light`
   * `DirectionalLight3D`

4. Normal semantics

   * Source selection.
   * Cardinality.
   * DATA coordinate space.
   * Normalization.
   * Explicit normal validation.
   * Generated normal formula.
   * Winding and degeneracy policy.

5. View3D lighting semantics

   * Ambient scalar.
   * Directional light direction convention.
   * Directional intensity.
   * DATA-space light behavior under camera/navigation changes.

6. Color and alpha formula

   * Base color source from S038.
   * Lambert scalar.
   * RGB multiplication and clamp.
   * Alpha passthrough.
   * Non-opaque alpha non-strict.

7. Color-space boundary

   * Protocol channel arithmetic only.
   * No linear RGB/sRGB/tone mapping/display-management claim.

8. Capability names

   * Accepted S039 names.
   * Existing accepted prerequisites.
   * Reserved/deferred names.

9. Diagnostics

   * Required validation diagnostics and recommended wording.

10. Backend conformance

    * Strict support.
    * Adapted review support.
    * Unsupported/deferred behavior.
    * Matplotlib rules.
    * Datoviz rules.
    * VisPy2 producer rules.

11. Fixtures

    * Positive fixtures.
    * Negative fixtures.
    * Capability advertisement gates.

12. Legacy compatibility notes

    * `shading="flat"` alias handling.
    * `shading="lambert"` non-canonical handling.
    * Existing optional fields are not authoritative unless normalized into S039.

13. Private/internal implementation boundaries

    * Backend-native material structs.
    * Shader slots.
    * Vulkan/draw-state names.
    * Matplotlib artists/axes/controllers.
    * Legacy GSP material classes.
    * Experimental texture/Phong paths.

14. **Risks and Stop Conditions**

S039 should remain ADR-only or defer Lambert if any of these conditions hold:

* The repo cannot define a canonical face count `F` for `MeshVisual` consistently enough to validate `(F,3)` normals.
* The accepted mesh spec does not guarantee canonical triangle faces, and the project is unwilling to restrict generated normals to triangles.
* The project wants vertex normals, smooth interpolation, or per-vertex Lambert in the same step.
* The project wants Phong/specular, light colors, textures, UVs, or material objects in S039.
* The project cannot prevent legacy `shading="lambert"` from silently meaning backend-specific behavior.
* Matplotlib or Datoviz support depends on backend-native material semantics that do not match the exact S039 formula.
* No backend can produce conformance fixtures for explicit normals, generated normals, winding reversal, zero/non-finite rejection, ambient-only, directional-only, and alpha passthrough.
* Color-space requirements expand into linear RGB, sRGB conversion, tone mapping, or display color management before the protocol is ready.
* Directional light semantics drift into camera-space or view-space headlights.
* Public API pressure requires Datoviz material structs, shader slots, Vulkan state, Matplotlib artists, or legacy GSP material classes to leak into the protocol.

The hard boundary is: **accept flat face-normal Lambert only if it stays a deterministic, DATA-space, backend-neutral protocol feature with exact validation and fixtures.** Otherwise, keep S039 deferred and continue with S038 unlit RGBA only.

