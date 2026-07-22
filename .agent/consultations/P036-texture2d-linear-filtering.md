# P036 - Texture2D Linear Filtering Protocol Shape

Date: 2026-07-22

Stage: post-S058 Datoviz v0.4-dev Texture2D follow-up

## Status

This needs ChatGPT Pro consultation.

Dependent public GSP linear-filtering implementation is paused until the user provides the
consultation result. The already implemented nearest-only S050 Datoviz path is independent and may
remain committed.

## Prompt

Paste the following single prompt into ChatGPT Pro:

```text
You are reviewing one narrow public protocol/API decision for GSP_API, a pre-1.0 Python scientific
visualization protocol with backend-neutral immutable scene records, separate renderers, and a
VisPy2-style producer. Answer as a senior graphics API and scientific-visualization architect.

Goal:
Decide the smallest correct extension that adds LINEAR texture filtering to the already accepted
nearest-only unlit Texture2D mesh contract. This is not a general sampler-design exercise. The
answer must be specific enough to write a small ADR/spec change and implement it without inventing
additional architecture.

Authority and existing accepted contract:

1. GSP is pre-1.0, so a deliberate source-compatible schema addition is acceptable, but capability
   claims remain explicit and fixture-backed. Backend-native objects and state are never public GSP
   semantics.

2. Existing immutable resource:

       enum Texture2DFormat { RGBA8 = "rgba8" }

       @dataclass(frozen=True, slots=True)
       class Texture2D:
           id: str
           image: numpy.ndarray[uint8]  # contiguous shape (H, W, 4), H/W > 0
           format: Texture2DFormat = Texture2DFormat.RGBA8

   Texture2D is document-local immutable pixel data, not a backend handle. `image[0]` is the top
   row. RGBA bytes normalize as byte/255. The accepted contract treats values as unmanaged numeric
   RGBA: it defines no sRGB decode, ICC handling, gamma correction, or display color management.

3. Existing mesh fields:

       enum MeshShading:
           UNLIT_RGBA = "unlit_rgba"
           FLAT_LAMBERT = "flat_lambert"
           TEXTURE2D_UNLIT = "texture2d_unlit"

       enum MeshUVMode:
           NONE = "none"
           VERTEX = "vertex"

       @dataclass(frozen=True, slots=True)
       class MeshVisual:
           id: str
           positions: float array (N,2) or (N,3)
           faces: integer array (M,3)
           coordinate_space: data or ndc
           color: uniform/per-face/per-vertex RGBA
           shading: MeshShading = UNLIT_RGBA
           texture2d_id: str | None = None
           uv_mode: MeshUVMode = NONE
           uvs: float array (N,2) | None = None
           # plus existing normal/depth/culling/order/transform fields

   `texture2d_unlit` requires a declared Texture2D, `uv_mode="vertex"`, finite `(N,2)` UVs, and a
   base mesh color. UVs use u left-to-right and v bottom-to-top; high v samples earlier/top image
   rows. Faces index positions and UVs together. Seams require duplicate vertices.

4. Existing S050 sampler is deliberately fixed:

       min filter = nearest
       mag filter = nearest
       wrap u/v = clamp_to_edge
       mipmaps = none
       LOD = base level only

   Existing specification says public linear filtering, repeat/mirror, border colors, anisotropy,
   mipmaps, LOD bias, public sampler objects, and backend sampler names are out of scope. Requests
   outside the accepted profile use `texture2d_sampler_unsupported`.

5. Existing material equation:

       tex = sample(texture, interpolated_uv)
       base = resolve_mesh_rgba(MeshVisual.color, MeshVisual.color_mode)
       output.rgb = clamp(base.rgb * tex.rgb, 0, 1)
       output.a   = clamp(base.a * tex.a, 0, 1)

   The material is unlit. Lights, normals, camera state, and backend material tint must not affect
   output. Strict opaque 3D conformance requires base alpha 1 and every texture alpha byte 255.

6. Existing capability names:

       texture2d.rgba8.v1
       meshvisual.uv.vertex2d.v1
       meshvisual.material.texture2d_unlit.v1
       gsp_vispy2.producer.mesh.texture2d_unlit.v1

   `meshvisual.material.texture2d_unlit.v1` currently means the fixed nearest/clamp/no-mipmap
   material. Protocol validation and renderer capability advertisement remain independent.

7. Existing producer API shape:

       Axes.mesh(
           positions,
           faces,
           *,
           color,
           color_mode=None,
           coordinate_space="data",
           shading="unlit_rgba",
           normal_mode=None,
           normals=None,
           normal_generation="none",
           order=0.0,
           transform=None,
           texture=None,
           uvs=None,
       )

   Supplying `texture` and `uvs` together creates a Texture2D and emits
   `shading="texture2d_unlit"`. Current producer documentation explicitly rejects `filter`,
   `sampler`, `wrap`, and `mipmap` arguments.

New Datoviz implementation evidence:

8. Local Datoviz v0.4-dev commit `be7f2a80354c25e85bab88c85f5ea7340975b569` adds public per-field-
   slot sampling:

       enum DvzFieldFilter { LINEAR = 0, NEAREST = 1 }

       DvzFieldSamplingDesc dvz_field_sampling_desc(void)
       DvzResult dvz_visual_set_field_sampling(
           DvzVisual* visual,
           const char* slot_name,
           const DvzFieldSamplingDesc* desc)

   The first Datoviz slice accepts matching min/mag LINEAR or matching min/mag NEAREST,
   clamp-to-edge only, and no mipmaps. Image `"field"` and mesh `"texture"` slots support both.
   Labels remain nearest-only. Sampling is correctly modeled per visual field slot, independently
   from binding the sampled-field resource. An older image-specific sampling helper remains a
   compatibility convenience and delegates to the field-slot API.

9. GSP now has a tested Datoviz nearest-only adapter. It uploads RGBA8 with Datoviz's linear-color
   role, flips v to adapt GSP's top-row/high-v convention, binds the mesh `"texture"` field, requests
   nearest min/mag, chooses the unlit material, and capability-gates on the new public API. A real
   S050 offscreen review rendered five Texture2D cases: UV orientation, nearest/clamp checker probes,
   vertex-color multiplication/seam, retained DATA-space View3D, and alpha diagnostics. Thus linear
   filtering is now technically available in Datoviz; the only blocker is defining public GSP
   semantics.

10. Matplotlib currently rejects all Texture2D meshes explicitly. Adding linear filtering must not
    require a Matplotlib texture rasterizer or cause Matplotlib to claim support.

Narrow design alternatives to decide:

A. Put a simple enum field on MeshVisual, for example
   `texture_filter: TextureFilter = TextureFilter.NEAREST`. This matches sampling as visual-slot
   state and lets two visuals sample the same immutable Texture2D differently.

B. Put `filter` on Texture2D. This is compact but couples immutable pixel data with sampling and
   prevents distinct sampling of one shared resource unless it is duplicated.

C. Add a public Sampler resource or separate min/mag fields. This is extensible but likely too broad
   for a two-filter, clamp-only, no-mipmap stage.

D. Change the fixed default globally from nearest to linear without adding a field. This is a
   semantic break, removes deterministic nearest behavior, and does not let users select both.

Questions:

1. Choose A, B, C, D, or a precisely stated alternative. Prefer the smallest backend-neutral model.
   Explain why the chosen ownership matches immutable resource sharing and visual-slot semantics.

2. Specify the exact enum and field names, Python types, default, validation, serialization, and
   applicability rules. Decide whether the field is legal only with `texture2d_unlit`, whether it
   must be absent/default for other shading modes, and whether one enum controls both minification
   and magnification for this bounded stage.

3. Preserve or revise capability semantics. In particular, decide whether the existing
   `meshvisual.material.texture2d_unlit.v1` should continue to mean nearest-only while a new
   capability such as `meshvisual.texture_filter.linear.v1` gates LINEAR, or whether another
   versioning scheme is more correct. Give exact capability names and prerequisites.

4. Define LINEAR sampling sufficiently for cross-backend conformance:
   - bilinear interpolation footprint and clamp-to-edge behavior;
   - interpolation of normalized unmanaged numeric RGBA code values;
   - whether filtering occurs before multiplication by interpolated base color;
   - expected tolerance/quantization for GPU and future CPU implementations;
   - behavior at texel centers, half-way boundaries, edges, and out-of-range UVs;
   - no mipmaps and one shared min/mag filter choice.
   Do not introduce sRGB decoding or broader color management unless it is unavoidable; if it is
   unavoidable, explain why.

5. Define the minimal diagnostics and negative tests. Decide how an incapable backend reports a
   valid LINEAR request without rejecting valid NEAREST payloads.

6. Decide whether the VisPy2 producer should add exactly one keyword such as
   `texture_filter="nearest"`, and state its exact signature/default/validation. It must lower to
   GSP protocol state and must not expose Datoviz names.

7. List the minimal positive automated fixtures needed before Datoviz advertises linear filtering.
   Include a 2x2 or similarly tiny texture with samples that distinguish linear from nearest,
   origin behavior, clamp behavior, color multiplication, alpha interpolation, and shared-texture
   different-filter behavior if the chosen model permits it.

8. State what remains deferred: independent min/mag, repeat/mirror/border wrap, mipmaps/LOD,
   anisotropy, sampler resources, texture mutation/streaming, sRGB/color management, perspective-
   correct UV interpolation if still outside the current contract, additional formats, and
   textured lighting.

Required output format:

Return exactly these sections:

1. Decision
   - One concise paragraph.

2. Public Protocol Surface
   - A table with exact enum/resource/field names, types, defaults, applicability, and semantics.

3. Normative Linear Sampling Rule
   - Precise ordered sampling and color-multiplication steps.
   - Numeric tolerance/quantization guidance suitable for conformance fixtures.

4. Capabilities And Diagnostics
   - A capability table with exact names and prerequisites.
   - A diagnostic table with triggers and required behavior.

5. Backward Compatibility
   - Explain behavior of all existing payloads and capability consumers.

6. Backend And Producer Behavior
   - Separate bullets for Datoviz, Matplotlib, and VisPy2.
   - Give the exact VisPy2 signature change if one is recommended.

7. Fixtures
   - Minimal positive fixtures.
   - Minimal negative fixtures.
   - State what must be runtime-proven before capability advertisement.

8. Deferred
   - Explicit list.

9. Implementation Plan
   - 4 to 6 small ordered commits/missions with acceptance criteria and stop conditions.

10. Final Recommendation
    - A compact normative schema snippet suitable for direct transfer into an ADR.
```

## Expected Result Handling

After the ChatGPT Pro result is pasted or committed:

1. Archive it as `.agent/consultations/P036-response.md`.
2. Review it against ADR-0029 and `spec/visuals/mesh_texture2d_unlit_s050.md`.
3. Amend or supersede the nearest-only contract with the smallest accepted extension.
4. Create an approved implementation mission before changing public protocol fields or VisPy2.
5. Keep repeat wrapping, mipmaps, independent min/mag filters, public sampler resources, and color
   management deferred unless the response provides a compelling compatibility reason otherwise.
