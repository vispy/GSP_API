1. Decision

The next accepted stage should be **unlit texture2D + per-vertex UVs for `MeshVisual`**, not smooth Lambert, Phong, alpha/culling, or broad VisPy2 3D ergonomics. It is the smallest remaining material expansion explicitly anticipated by the current boundary: S039 already covered flat Lambert with face normals, while vertex normals/smooth Lambert would expand interpolation and lighting semantics, Phong would introduce a real material model, and alpha/culling/query work belongs to separate rendering-state or readback tracks. The stage should add only value-style RGBA8 texture resources, vertex UVs, and one unlit texture material mode, with fixed sampler semantics and strict capability gating. 

2. Accepted Protocol Surface

| Surface                      |                                                                        Type / default | Semantics                                                                                                                                                                                                                                                                                                                                                       |                                                                                                                                                                                                                                |
| ---------------------------- | ------------------------------------------------------------------------------------: | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `Texture2D` resource         |                                               Document-local immutable value resource | A backend-neutral texture value, not a backend handle, shader object, material object, Vulkan object, Matplotlib artist, or Datoviz slot. May be shared by multiple visuals within one resolved payload by ID. No mutation, streaming, subimage upload, external file path, URI, or lifecycle API in v1.                                                        |                                                                                                                                                                                                                                |
| `Texture2D.id`               |                                                    `str`, required, unique in payload | Document-local resource identifier. Must be resolved before rendering. Unknown IDs are validation errors.                                                                                                                                                                                                                                                       |                                                                                                                                                                                                                                |
| `Texture2D.format`           |                                                         enum, fixed/default `"rgba8"` | Only 8-bit straight-alpha RGBA is accepted. No RGB, grayscale, float, uint16, premultiplied alpha, compressed textures, depth textures, normal maps, or backend-native formats.                                                                                                                                                                                 |                                                                                                                                                                                                                                |
| `Texture2D.image`            |                                  `uint8` array, shape `(H, W, 4)`, `H >= 1`, `W >= 1` | Pixel data. `image[0, :, :]` is the top image row. Values are normalized as `byte / 255.0` for sampling. No implicit rescaling, color-profile conversion, dtype conversion, channel expansion, or alpha premultiplication.                                                                                                                                      |                                                                                                                                                                                                                                |
| Texture color-space boundary |                                                       Fixed semantic, no public field | `rgba8` is treated as unmanaged numeric RGBA code values. The protocol does not define sRGB decode, linear-light conversion, ICC profiles, gamma-correct filtering, display color management, or perceptual blending. Backends must not use sRGB texture formats if that changes the numeric rule.                                                              |                                                                                                                                                                                                                                |
| `MeshVisual.shading`         | add canonical enum value `"texture2d_unlit"`; default remains existing `"unlit_rgba"` | Selects the new material. It is mutually exclusive with `flat_lambert`. Normals, lights, camera position, view direction, specular terms, generated attributes, or backend-native material state must not affect color. No legacy alias should be introduced in this stage.                                                                                     |                                                                                                                                                                                                                                |
| `MeshVisual.texture2d_id`    |                                                                                  `str | None`, default `None`                                                                                                                                                                                                                                                                                                                                           | Required when `shading == "texture2d_unlit"`. References a `Texture2D` resource. Must be absent or `None` for strict `unlit_rgba` and `flat_lambert` unless a later accepted material consumes it.                             |
| `MeshVisual.uv_mode`         |                                                                          enum `"none" | "vertex"`, default `"none"`                                                                                                                                                                                                                                                                                                                                     | `vertex` means UVs are indexed by the existing mesh vertex indices. No separate UV index buffer, no per-corner UVs, no face-varying UVs, no generated UVs. Texture seams require duplicated positions with distinct UV values. |
| `MeshVisual.uvs`             |                                                            finite float array `(N, 2) | None`, default `None`                                                                                                                                                                                                                                                                                                                                           | Required when `uv_mode == "vertex"` and `shading == "texture2d_unlit"`. `N` must equal `len(positions)`. `uvs[i]` belongs to `positions[i]`; `faces` index both positions and UVs.                                             |
| UV coordinate convention     |                                                                        Fixed semantic | `u` increases left to right. `v` increases bottom to top. Texture coordinate `(0, 0)` is the bottom-left texture edge; `(1, 1)` is the top-right texture edge. For a `2x2` texture, texel centers are approximately `(0.25, 0.25)`, `(0.75, 0.25)`, `(0.25, 0.75)`, `(0.75, 0.75)`. Since `image[0]` is the top row, `(0.25, 0.75)` samples the top-left texel. |                                                                                                                                                                                                                                |
| UV interpolation             |                                           Barycentric interpolation over the triangle | UVs are interpolated affinely across each triangle. This is sufficient for the accepted orthographic View3D baseline. Perspective-correct texturing remains deferred because perspective camera/projection semantics are not accepted here.                                                                                                                     |                                                                                                                                                                                                                                |
| Sampler                      |                                              No public sampler object or fields in v1 | Fixed sampler: `nearest` minification, `nearest` magnification, `clamp_to_edge` in both `u` and `v`, base level only. No linear filtering, repeat, mirrored repeat, border color, anisotropy, mipmap generation, LOD bias, or backend sampler exposure.                                                                                                         |                                                                                                                                                                                                                                |
| Sampling rule                |                                                                        Fixed semantic | `tex = sample_nearest_clamp(texture, interpolated_uv)`, with `tex.rgba = image_byte / 255.0`. Fixtures should sample away from triangle and texel boundaries to avoid edge ambiguity.                                                                                                                                                                           |                                                                                                                                                                                                                                |
| Color multiplication rule    |                                                                        Fixed semantic | Resolve `base` exactly as existing `MeshVisual.color` / `color_mode` would for `unlit_rgba`; then `output.rgb = clamp(base.rgb * tex.rgb, 0, 1)`. No lighting term is applied.                                                                                                                                                                                  |                                                                                                                                                                                                                                |
| Alpha rule                   |                                                                        Fixed semantic | Straight alpha only: `output.a = clamp(base.a * tex.a, 0, 1)`. Alpha is not lit. For strict opaque 3D conformance, require `base.a == 1` and all texture alpha bytes equal `255`; otherwise rendering may proceed only under existing non-strict alpha diagnostics and must not claim strict opaque depth behavior.                                             |                                                                                                                                                                                                                                |
| Depth, culling, order        |                                                                  Existing fields only | No new depth, sorting, culling, transparency, or draw-order semantics are introduced. Existing `depth_test`, `depth_write`, `face_culling`, and `order` rules remain unchanged and separately capability-gated.                                                                                                                                                 |                                                                                                                                                                                                                                |

3. Capability Names And Diagnostics

| Capability                                        | Meaning                                                                                                                                      | Prerequisites / notes                                                                                                                                                |
| ------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `texture2d.rgba8.v1`                              | Backend/protocol can validate and resolve document-local immutable `Texture2D` resources with `uint8 (H, W, 4)` data.                        | Does not by itself claim textured mesh rendering.                                                                                                                    |
| `meshvisual.uv.vertex2d.v1`                       | Backend/protocol accepts per-vertex UVs of shape `(N, 2)` indexed by existing mesh faces.                                                    | No separate UV indices or per-corner UVs.                                                                                                                            |
| `meshvisual.material.texture2d_unlit.v1`          | Backend renders `MeshVisual.shading == "texture2d_unlit"` using fixed nearest/clamp/no-mipmap sampling and multiplicative unlit RGBA output. | Requires `texture2d.rgba8.v1` and `meshvisual.uv.vertex2d.v1`. Does not imply Lambert, Phong, normal maps, texture arrays, alpha sorting, culling, or model loading. |
| `vispy2.producer.mesh.texture2d_unlit.v1`         | Producer-only claim that VisPy2 can emit canonical GSP textured mesh payloads and validate their inputs.                                     | Not a renderer capability. `render_matplotlib()` or other render calls must still check renderer capabilities.                                                       |
| Existing `meshvisual.positions3d.opaque_depth.v1` | Strict opaque 3D depth for DATA-space View3D meshes.                                                                                         | May be combined with textured meshes only when final alpha is conservatively known opaque: base alpha `1` and texture alpha channel all `255`.                       |

| Diagnostic                                        | Condition                                                                                                                                             | Required behavior                                                                                                                 |
| ------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| `texture2d_invalid_resource`                      | Missing `id`, duplicate `id`, empty image, invalid shape, invalid dtype, unsupported format, or invalid channel count.                                | Reject strict payload. Do not coerce silently.                                                                                    |
| `texture2d_unknown_id`                            | `MeshVisual.texture2d_id` references no declared `Texture2D`.                                                                                         | Reject strict payload.                                                                                                            |
| `texture2d_resource_limit_exceeded`               | Texture dimensions or total texture memory exceed backend limits.                                                                                     | Fail with diagnostic; no silent downscaling or format conversion.                                                                 |
| `meshvisual_texture_required`                     | `shading == "texture2d_unlit"` but `texture2d_id` is absent.                                                                                          | Reject strict payload.                                                                                                            |
| `meshvisual_uv_required`                          | `shading == "texture2d_unlit"` but `uv_mode != "vertex"` or `uvs` is absent.                                                                          | Reject strict payload.                                                                                                            |
| `meshvisual_uv_shape_mismatch`                    | `uvs` is not shape `(N, 2)` for the mesh positions.                                                                                                   | Reject strict payload.                                                                                                            |
| `meshvisual_uv_nonfinite`                         | Any UV coordinate is `NaN` or infinite.                                                                                                               | Reject strict payload.                                                                                                            |
| `meshvisual_uv_topology_unsupported`              | Payload requests separate UV indices, per-face UVs, per-corner UVs, generated UVs, or another UV cardinality.                                         | Reject unless a later capability explicitly accepts it.                                                                           |
| `meshvisual_material_texture2d_unlit_unsupported` | Renderer lacks `meshvisual.material.texture2d_unlit.v1`.                                                                                              | Reject or return explicit unsupported-capability diagnostic. Do not render as flat color silently.                                |
| `texture2d_sampler_unsupported`                   | Payload requests linear filtering, repeat wrap, mipmaps, border color, anisotropy, or another sampler state.                                          | Reject in v1.                                                                                                                     |
| `texture2d_colorspace_unsupported`                | Payload requests sRGB decode, ICC profiles, linear-light conversion, or other color-management semantics.                                             | Reject in v1.                                                                                                                     |
| `meshvisual_texture_lighting_conflict`            | Payload combines `texture2d_unlit` with public material/light/normal semantics intended to affect color, such as Lambert or Phong texture modulation. | Reject in v1. Lights may exist in the `View3D`, but they must not affect this material.                                           |
| `mesh3d_alpha_not_strict`                         | Textured 3D mesh has base alpha `< 1` or any texture alpha byte `< 255`.                                                                              | Rendering is non-strict for final 3D compositing; backend must not advertise/use strict opaque-depth conformance for that visual. |

4. Backend Conformance

* **Matplotlib**

  * Should **not** advertise `meshvisual.material.texture2d_unlit.v1` using the current CPU projection plus face-sorting 3D mesh path.
  * Existing `Poly3DCollection`-style face coloring is not texture mapping and must not be treated as a compliant fallback.
  * Matplotlib may continue to reject textured mesh payloads with `meshvisual_material_texture2d_unlit_unsupported`.
  * It may advertise this capability only if a fixture-backed CPU triangle texture rasterizer is added that implements the accepted UV interpolation, nearest/clamp sampling, orientation convention, color multiplication, and alpha diagnostics. That would still not promote Matplotlib to strict fragment-depth 3D unless the existing opaque-depth requirements are independently met.

* **Datoviz**

  * May advertise `texture2d.rgba8.v1`, `meshvisual.uv.vertex2d.v1`, and `meshvisual.material.texture2d_unlit.v1` only through public Datoviz APIs that expose canonical RGBA8 texture data and canonical per-vertex UVs.
  * Must not use private Vulkan state, private shader slots, private mesh IDs, or non-authoritative backend identifiers as part of the public GSP semantics.
  * For strict 3D, textured meshes may combine with `meshvisual.positions3d.opaque_depth.v1` only on the retained DATA-space View3D path, with native depth test/write enabled and conservative opacity satisfied.
  * If Datoviz supports only linear filtering, repeat wrap, mipmaps, bottom-left image origin, or sRGB decode in a way that cannot be configured to match v1 semantics, it must not advertise the v1 material capability.

* **Producer-only / VisPy2 behavior**

  * VisPy2 may add only a thin producer convenience that lowers to canonical GSP `Texture2D`, `MeshVisual.uvs`, `uv_mode="vertex"`, and `shading="texture2d_unlit"`.
  * VisPy2 must not expose backend-native textures, samplers, shader names, Datoviz slots, Matplotlib artists, material classes, draw-call names, or controller objects.
  * `fig.render_matplotlib()` must check renderer capabilities and fail/diagnose rather than silently dropping the texture.
  * Producer capability is separate from renderer capability: VisPy2 may be able to emit a valid textured mesh even when the selected renderer cannot render it.

5. VisPy2 API

Add no broad 3D ergonomics, no public camera/navigation API, no material object, and no sampler object in this stage.

After the GSP protocol and validator land, VisPy2 may extend the existing `Axes.mesh` signature only as follows:

```python
def mesh(
    self,
    positions,
    faces,
    *,
    color=(1.0, 1.0, 1.0, 1.0),
    color_mode=None,
    coordinate_space="data",
    order=0.0,
    texture=None,
    uvs=None,
):
    ...
```

Required VisPy2 semantics:

* `texture is None and uvs is None`: preserve current behavior exactly.
* `texture is not None and uvs is not None`: emit one GSP `Texture2D` resource, set `MeshVisual.texture2d_id`, `uv_mode="vertex"`, `uvs=uvs`, and `shading="texture2d_unlit"`.
* `texture` must be array-like coercible only to strict `uint8 (H, W, 4)` without semantic conversion. No filename, PIL object, URI, RGB expansion, float scaling, or color-profile handling in v1.
* `uvs` must be finite shape `(N, 2)`.
* `color` remains the multiplicative base color. Default white means the texture is shown unchanged.
* Supplying exactly one of `texture` or `uvs` is an error.
* No `shading`, `sampler`, `wrap`, `filter`, `mipmap`, `material`, `normal`, `light`, `depth_state`, `culling`, `texture_id`, or backend-specific keyword should be added to the public VisPy2 API in this stage.

6. Fixtures

**Positive fixtures**

* Single NDC triangle with a `2x2` RGBA8 texture, UVs at texel centers, white base color, and sampled interior pixels verifying UV orientation:

  * top-left texture row maps to high `v`;
  * bottom-left maps to low `v`;
  * `u` increases left to right.
* Two-triangle quad in NDC with a `4x4` checker texture, white base color, nearest sampling, and clamp-to-edge UVs.
* DATA-space View3D orthographic opaque textured quad, fully opaque texture alpha, native depth enabled where applicable, verifying compatibility with existing opaque-depth rules.
* Two overlapping opaque textured DATA-space meshes at different depths, verifying that texture material does not alter accepted strict depth behavior on backends that already advertise opaque depth.
* Color multiplication fixture: uniform base color multiplied by known RGBA8 texels, sampled away from edges.
* Vertex duplication seam fixture: two triangles share spatially coincident positions duplicated as separate vertices with different UVs, proving that v1 seam representation is duplicate-position based.
* Clamp fixture: UVs outside `[0, 1]` sample edge texels under `clamp_to_edge`.
* Alpha diagnostic fixture: texture contains at least one alpha byte `< 255`; material output alpha is multiplication, but 3D compositing is marked non-strict.

**Negative fixtures**

* `shading="texture2d_unlit"` with no `texture2d_id`.
* `shading="texture2d_unlit"` with unknown `texture2d_id`.
* Texture image shape `(H, W, 3)`, `(H, W)`, `(H, W, 1)`, or `(H, W, 4, 1)`.
* Texture dtype `float32`, `float64`, `uint16`, `int32`, or boolean.
* Empty texture dimensions.
* `uvs` missing, wrong shape, wrong length, or containing `NaN` / `inf`.
* Payload requesting separate UV indices, per-corner UVs, generated UVs, or face-varying UVs.
* Payload requesting linear filtering, repeat wrap, mipmaps, sRGB decode, border color, anisotropy, or a sampler object.
* Payload combining texture material with `flat_lambert`, Phong/specular fields, normal maps, or any material/light semantics intended to affect the texture color.
* Backend without `meshvisual.material.texture2d_unlit.v1` receives a textured mesh and must fail/diagnose rather than render untextured geometry.
* Non-opaque textured 3D mesh attempting to claim strict opaque-depth conformance.

**Manual visual review artifacts if needed**

* UV orientation plate with labeled colored quadrants: top-left, top-right, bottom-left, bottom-right.
* Checkerboard textured quad rendered at large size, with sampling probes away from triangle and texel boundaries.
* Duplicate-vertex seam plate showing a deliberate UV discontinuity.
* Color multiplication swatch plate: white base, half-red base, half-alpha base.
* Backend comparison PNGs for Datoviz and any future Matplotlib CPU raster path, with tolerances based on interior sample points rather than full-image exact hashes.

7. Deferred

The following must remain out of scope after this stage:

* Phong, Blinn-Phong, specular color, shininess, roughness, metallic/roughness, PBR, or public material objects.
* Smooth Lambert, vertex normals, normal interpolation, normal generation beyond accepted face-flat generation, tangent frames, normal maps, bump maps, displacement maps.
* Textured Lambert or any lighting applied to texture samples.
* Multiple textures, texture arrays, 3D textures, cube maps, atlas metadata, external image files, compressed textures, float textures, RGB textures, grayscale textures, depth textures.
* Public sampler objects, linear filtering, repeat/mirror wrap, border colors, mipmaps, anisotropy, LOD controls.
* Strict alpha/transparency semantics, transparency sorting, order-independent transparency, premultiplied-alpha policy, alpha test/discard, cutout materials.
* Culling expansion beyond separately accepted capability-gated `back` / `front`.
* Model loading, OBJ/glTF import, material libraries, asset graphs.
* Instancing, mesh-local transforms, matrix-first authoring, scene graphs, hierarchical nodes.
* Backend-native camera/controllers, Datoviz slots, Vulkan state, Matplotlib artists, shader names, draw calls.
* Expanded 3D query payloads, mesh triangle picking expansion, private backend face IDs, or any picking semantics blocked by the Datoviz canonical triangle identity issue.
* Perspective camera texturing or perspective-correct interpolation.
* Non-mesh 3D visual families.

8. Implementation Mission Plan

9. **ADR/spec mission: `texture2d_unlit` protocol boundary**

   * Acceptance criteria: ADR defines `Texture2D`, `MeshVisual.texture2d_id`, `uv_mode`, `uvs`, `shading="texture2d_unlit"`, fixed sampler semantics, UV convention, color/alpha rule, capabilities, and diagnostics.
   * Stop condition: any requirement emerges for public material objects, public sampler objects, backend handles, model loading, or lighting-texture interaction.

10. **Protocol validator mission**

    * Acceptance criteria: validator accepts all positive structural cases and rejects all negative fixtures for texture resources, UV cardinality, unsupported sampler/color-space requests, and missing capabilities.
    * Stop condition: validator needs backend-specific coercion or accepts unsupported fields silently.

11. **Reference fixture generator mission**

    * Acceptance criteria: fixture generator produces deterministic small RGBA8 textures, UV arrays, expected sample probes, and reference images/probe values for NDC and orthographic View3D cases.
    * Stop condition: tests depend on full-image exact matching at triangle edges or on backend-specific antialiasing behavior.

12. **Datoviz public-API feasibility mission**

    * Acceptance criteria: demonstrate texture resource upload, per-vertex UV binding, nearest/clamp/no-mipmap sampling, correct image orientation, and fixture conformance using only public Datoviz APIs.
    * Stop condition: implementation requires private Vulkan objects, private shader slots, private mesh IDs, or unverifiable sampler/color-space behavior.

13. **Datoviz capability advertisement mission**

    * Acceptance criteria: advertise `texture2d.rgba8.v1`, `meshvisual.uv.vertex2d.v1`, and `meshvisual.material.texture2d_unlit.v1` only after automated fixtures pass; combine with strict opaque-depth only under conservative alpha and existing retained DATA-space View3D constraints.
    * Stop condition: any alpha, culling, sorting, or picking semantics must be expanded to make the fixture pass.

14. **Matplotlib policy mission**

    * Acceptance criteria: Matplotlib explicitly does not advertise textured mesh capabilities; unsupported textured payloads produce clear diagnostics. Optional future CPU rasterization is documented as a separate mission, not a fallback.
    * Stop condition: implementation attempts to approximate textures using face colors or silently drops texture fields.

15. **VisPy2 thin producer mission**

    * Acceptance criteria: `Axes.mesh(..., texture=None, uvs=None)` lowers to canonical GSP only when both are supplied; validates dtype/shape/cardinality; does not add sampler/material/backend keywords; renderer calls check capabilities.
    * Stop condition: API design starts exposing high-level 3D navigation, material classes, texture IDs, backend handles, file loading, or shading controls.

16. **Capability/docs audit mission**

    * Acceptance criteria: all advertised backend and producer capabilities are fixture-backed; docs state exact limitations, deferred concepts, alpha non-strict behavior, and UV seam duplication requirement.
    * Stop condition: documentation implies support for Phong, smooth normals, model files, alpha sorting, repeated textures, or backend-native material control.

17. Risks / Open Questions

* Whether Datoviz can expose the required texture and UV path through stable public APIs without relying on private shader or slot details.
* Whether Datoviz can force nearest filtering, clamp-to-edge, no mipmaps, unmanaged RGBA8 sampling, and the specified image-origin convention exactly enough for conformance.
* Matplotlib likely cannot support this stage without a custom CPU textured-triangle rasterizer; that should not block the protocol but means Matplotlib must initially reject the capability.
* The unmanaged color-space rule is deliberately conservative; later sRGB/linear semantics would require a separate capability and new fixtures.
* Per-vertex UVs force duplicated vertices for seams. This is acceptable for v1 but awkward for imported models, which is another reason model loading and separate UV indices must remain deferred.
* Texture alpha can make otherwise opaque meshes non-strict. The conservative “all texture alpha bytes must be 255” rule may reject some technically opaque sampled regions, but it keeps capability claims simple and safe.
* Pixel-exact cross-backend image comparison may be fragile at triangle edges; conformance should rely on interior probe points and dedicated manual review plates where necessary.

