# P036 Response - Texture2D Linear Filtering Protocol Shape

Date received: 2026-07-22

Source: ChatGPT Pro consultation response to `P036-texture2d-linear-filtering.md`.

## 1. Decision

Choose **A**: add a visual-owned `MeshVisual.texture_filter` field using a two-value `TextureFilter` enum. `Texture2D` must remain immutable document-local pixel data; sampling is state of the visual’s texture field slot, so two visuals may sample the same resource differently. This matches Datoviz’s public per-visual-field sampling model and avoids prematurely introducing sampler resources, independent min/mag filters, or backend-native state. The default remains `NEAREST`, preserving the complete S050 contract.  

## 2. Public Protocol Surface

| Surface                     | Exact definition                                                | Default and serialization                                                                                                                                                     | Applicability                                             | Semantics                                                                                                                 |
| --------------------------- | --------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------- |
| `TextureFilter`             | `enum TextureFilter { NEAREST = "nearest"; LINEAR = "linear" }` | Serialized as the lower-case strings `"nearest"` and `"linear"`                                                                                                               | Initially used only by `MeshVisual.texture_filter`        | Selects one filter for both minification and magnification                                                                |
| `MeshVisual.texture_filter` | `texture_filter: TextureFilter = TextureFilter.NEAREST`         | Serialized key: `"texture_filter"`. Missing and explicit `"nearest"` both decode as `NEAREST`. Canonical encoders should omit the key for `NEAREST` and emit it for `LINEAR`. | Active only when `shading == MeshShading.TEXTURE2D_UNLIT` | `NEAREST`: existing fixed S050 sampling. `LINEAR`: base-level bilinear sampling. Both retain clamp-to-edge and no mipmaps |
| `Texture2D`                 | Unchanged                                                       | Unchanged                                                                                                                                                                     | Shared immutable resource                                 | Contains only RGBA8 pixel data and format; it acquires no sampling state                                                  |

Implementation should append `texture_filter` as a defaulted field at the end of the Python dataclass to avoid shifting existing positional constructor parameters. Documentation may display it next to `texture2d_id`, `uv_mode`, and `uvs`.

Validation rules:

1. For `shading == TEXTURE2D_UNLIT`, both `NEAREST` and `LINEAR` are valid.
2. For every other shading mode, the field must be absent or equal to `NEAREST`. `LINEAR` is invalid because no texture field slot is active.
3. Unknown serialized values are ordinary enum-validation errors.
4. Existing `texture2d_unlit` requirements remain unchanged: declared texture, vertex UVs, finite `(N, 2)` values, and base mesh color.
5. The enum controls both minification and magnification. There are no separate public min/mag fields.
6. Wrap remains clamp-to-edge, mipmaps remain absent, and sampling remains restricted to the base level. 

## 3. Normative Linear Sampling Rule

For a fragment with interpolated texture coordinates `(u, v)`, a texture of width `W`, height `H`, and top-to-bottom array row index `j`, define:

```text
uc = clamp(u, 0, 1)
vc = clamp(v, 0, 1)

x = W * uc       - 0.5
y = H * (1 - vc) - 0.5

px = floor(x)
py = floor(y)

fx = x - px
fy = y - py

i0 = clamp(px,     0, W - 1)
i1 = clamp(px + 1, 0, W - 1)
j0 = clamp(py,     0, H - 1)
j1 = clamp(py + 1, 0, H - 1)
```

For each RGBA channel, first normalize the four source bytes:

```text
C[j, i] = image[j, i] / 255
```

Then compute the base-level bilinear sample:

```text
top    = (1 - fx) * C[j0, i0] + fx * C[j0, i1]
bottom = (1 - fx) * C[j1, i0] + fx * C[j1, i1]
tex    = (1 - fy) * top       + fy * bottom
```

The ordered material evaluation is:

1. Obtain the fragment UV using the existing mesh UV interpolation contract.

2. Clamp the finite UV to the texture domain.

3. Normalize RGBA8 texels as unmanaged numeric values using `byte / 255`.

4. Bilinearly interpolate all four channels independently. RGB is not premultiplied by alpha before filtering.

5. Resolve the fragment’s base mesh RGBA using the existing color-mode and interpolation rules.

6. Multiply only after texture filtering:

   ```text
   output.rgb = clamp(base.rgb * tex.rgb, 0, 1)
   output.a   = clamp(base.a   * tex.a,   0, 1)
   ```

7. Apply the existing framebuffer conversion and compositing rules.

No sRGB decoding, gamma correction, ICC transformation, or other color management occurs.

The following coordinates are normative:

* Texel `(i, j)` has center:

  ```text
  u = (i + 0.5) / W
  v = 1 - (j + 0.5) / H
  ```

* At a texel center, `LINEAR` returns that texel exactly before implementation quantization.

* Halfway between adjacent centers, the two texels contribute equally along that axis.

* Halfway in both axes, the four texels contribute equally.

* `u = 0`, `u = 1`, `v = 0`, `v = 1`, and all finite out-of-range UVs use replicated edge texels; no border value participates.

* Minification and magnification use the same base-level bilinear rule. No mip level is selected.

The normative reference result is the real-valued formula above. Conformance does not require bit-identical fixed-function arithmetic. For an unblended normalized or RGBA8 readback, each channel must satisfy:

```text
abs(actual_normalized - reference_normalized) <= 2 / 255
```

This tolerance covers interpolation-weight precision and final normalized-output quantization. Fixtures must sample stable interior fragments, avoid geometry edges, disable blending when verifying material alpha, and avoid nearest-filter probes exactly on nearest-selection boundaries.

## 4. Capabilities And Diagnostics

### Capabilities

| Capability                                          | Status    | Exact guarantee                                                                            | Prerequisites                                                               |
| --------------------------------------------------- | --------- | ------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------- |
| `texture2d.rgba8.v1`                                | Unchanged | Supports immutable RGBA8 `Texture2D` resources                                             | Existing resource support                                                   |
| `meshvisual.uv.vertex2d.v1`                         | Unchanged | Supports per-vertex `(N, 2)` UVs                                                           | Existing `MeshVisual` support                                               |
| `meshvisual.material.texture2d_unlit.v1`            | Unchanged | Supports the original nearest/clamp/no-mipmap `texture2d_unlit` profile                    | `texture2d.rgba8.v1`, `meshvisual.uv.vertex2d.v1`                           |
| `meshvisual.texture_filter.linear.v1`               | **New**   | Correctly renders `texture_filter="linear"` using the rule in section 3                    | All three capabilities above                                                |
| `gsp_vispy2.producer.mesh.texture2d_unlit.v1`       | Unchanged | Produces the original default-nearest textured mesh records                                | Existing producer prerequisites                                             |
| `gsp_vispy2.producer.mesh.texture_filter.linear.v1` | **New**   | Accepts the public `texture_filter="linear"` producer keyword and emits the protocol field | `gsp_vispy2.producer.mesh.texture2d_unlit.v1` and the new schema enum/field |

`meshvisual.material.texture2d_unlit.v1` retains its existing guarantee: nearest filtering works. It does not imply LINEAR support. A renderer must not advertise `meshvisual.texture_filter.linear.v1` without also advertising the three renderer prerequisites. No `v2` material capability is needed. 

The producer capability is independent of renderer support. End-to-end applications must intersect the producer’s capabilities with the selected renderer’s capabilities.

### Diagnostics

| Diagnostic                                                              | Trigger                                                                                               | Required behavior                                                                                  |
| ----------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------- |
| Existing enum-validation diagnostic                                     | `texture_filter` has a non-string or an unknown string such as `"cubic"`                              | Reject during protocol decoding or validation; do not treat it as a backend capability failure     |
| `meshvisual_texture_filter_inapplicable`                                | `texture_filter == LINEAR` while `shading != TEXTURE2D_UNLIT`                                         | Reject as an invalid `MeshVisual`; do not silently ignore the non-default request                  |
| Existing texture-material validation diagnostics                        | `TEXTURE2D_UNLIT` lacks a valid texture, UV mode, UV array, or base color                             | Preserve current behavior; do not replace these errors with a filter diagnostic                    |
| `texture2d_sampler_unsupported`                                         | A protocol-valid LINEAR visual reaches a renderer that lacks `meshvisual.texture_filter.linear.v1`    | Report the unsupported requested filter and required capability. Never downgrade LINEAR to NEAREST |
| `texture2d_sampler_unsupported` or the existing producer argument error | A caller requests deferred sampler features such as wrapping, mipmaps, or independent min/mag filters | Preserve the existing rejection behavior; do not infer a public sampler model                      |

A renderer that supports only the existing material capability must continue accepting valid NEAREST visuals. The missing LINEAR capability applies only to visuals requesting `LINEAR`.

## 5. Backward Compatibility

All existing serialized payloads omit `texture_filter`; they therefore decode as `TextureFilter.NEAREST` and render exactly as before. Existing nearest/clamp/no-mipmap fixtures remain normative and require no semantic update.

Appending a defaulted field preserves existing Python construction patterns. Canonical omission of the default also prevents newly serialized NEAREST records from acquiring unnecessary wire differences.

Existing capability consumers remain valid:

* A consumer checking only `meshvisual.material.texture2d_unlit.v1` may continue generating or submitting NEAREST visuals.
* A consumer requesting LINEAR must additionally require `meshvisual.texture_filter.linear.v1`.
* Existing renderers need not implement LINEAR and must not advertise the new capability.
* A renderer may advertise both capabilities, but never the LINEAR capability alone.
* No existing capability is renamed or re-versioned.
* `Texture2D` identity, equality, sharing, and immutability are unchanged.

New LINEAR payloads are deliberately outside the execution contract of old nearest-only renderers. They remain protocol-valid under the revised schema but require capability negotiation or the specified unsupported-sampler diagnostic.

## 6. Backend And Producer Behavior

* **Datoviz**

  * Continue uploading RGBA8 with the existing linear numeric-color role and continue flipping `v` to adapt GSP’s top-row/high-`v` convention.
  * Configure the mesh visual’s `"texture"` field through `dvz_visual_set_field_sampling()`.
  * For `NEAREST`, explicitly request matching nearest min/mag values.
  * For `LINEAR`, explicitly request matching linear min/mag values.
  * Retain clamp-to-edge and no mipmaps.
  * Apply sampling state per visual field slot, independently of resource binding, so one uploaded texture can serve visuals with different filters.
  * Never expose `DvzFieldFilter`, slot names, or other Datoviz vocabulary through GSP.
  * Advertise the new capability only after real offscreen runtime conformance succeeds. The available Datoviz API already models this state at the appropriate field-slot level. 

* **Matplotlib**

  * Make no texture-rasterization change.
  * Continue explicitly rejecting all `Texture2D` mesh visuals, whether NEAREST or LINEAR.
  * Advertise neither `meshvisual.material.texture2d_unlit.v1` nor `meshvisual.texture_filter.linear.v1`.
  * Merely recognizing the new schema field must not be interpreted as rendering support. 

* **VisPy2**

  * Add exactly one keyword-only argument:

    ```python
    def mesh(
        self,
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
        texture_filter: Literal["nearest", "linear"] = "nearest",
    ):
        ...
    ```

  * Accept only `"nearest"` and `"linear"`; any other value raises `ValueError`.

  * When `texture` and `uvs` are supplied together, lower the value to `MeshVisual.texture_filter` while emitting `shading="texture2d_unlit"`.

  * `texture_filter="nearest"` without a textured mesh is an inert default.

  * `texture_filter="linear"` without both `texture` and `uvs` raises `ValueError`.

  * Continue rejecting `filter`, `sampler`, `wrap`, and `mipmap` arguments.

  * Do not expose Datoviz enum names or backend objects.

  * Advertise `gsp_vispy2.producer.mesh.texture_filter.linear.v1` once this lowering path is tested. The current producer surface and its explicit sampler-argument exclusions otherwise remain unchanged. 

## 7. Fixtures

Use this shared 2×2 RGBA8 texture, with `image[0]` as the top row:

| Location     | Array index |                  RGBA8 | Normalized RGBA |
| ------------ | ----------: | ---------------------: | --------------: |
| Top-left     |    `[0, 0]` |     `(255, 0, 0, 255)` |  `(1, 0, 0, 1)` |
| Top-right    |    `[0, 1]` |       `(0, 255, 0, 0)` |  `(0, 1, 0, 0)` |
| Bottom-left  |    `[1, 0]` |       `(0, 0, 255, 0)` |  `(0, 0, 1, 0)` |
| Bottom-right |    `[1, 1]` | `(255, 255, 255, 255)` |  `(1, 1, 1, 1)` |

### Minimal positive fixtures

1. **`texture2d_linear_centers_orientation_2x2`**

   * White base color.
   * Probe `(0.25, 0.75)`, `(0.75, 0.75)`, `(0.25, 0.25)`, and `(0.75, 0.25)`.
   * Expect the four exact texels within tolerance.
   * This proves that high `v` addresses the top image row.

2. **`texture2d_linear_interpolation_clamp_2x2`**

   * White base color.
   * At `(0.5, 0.5)`, expect `(0.5, 0.5, 0.5, 0.5)`.
   * At `(0.375, 0.625)`, expect `(0.625, 0.25, 0.25, 0.625)`.
   * At `(-0.25, 1.25)`, expect top-left `(1, 0, 0, 1)`.
   * At `(1.25, -0.25)`, expect bottom-right `(1, 1, 1, 1)`.
   * Exercise both magnified and minified geometry so the same LINEAR setting is proven for both paths, always at base level.

3. **`texture2d_linear_color_alpha_multiplication`**

   * Probe `(0.375, 0.625)`.

   * Use base RGBA `(0.8, 0.4, 0.5, 0.5)`.

   * Texture sample is `(0.625, 0.25, 0.25, 0.625)`.

   * Expected material output is:

     ```text
     (0.5, 0.1, 0.125, 0.3125)
     ```

   * Observe the unblended material output or disable blending.

4. **`texture2d_shared_resource_distinct_filters`**

   * Bind the same `Texture2D.id` to two visuals with identical geometry and UV `(0.375, 0.625)`.
   * NEAREST visual expects top-left `(1, 0, 0, 1)`.
   * LINEAR visual expects `(0.625, 0.25, 0.25, 0.625)`.
   * This proves that filter state belongs to the visual slot rather than the immutable resource.

Existing S050 NEAREST fixtures remain mandatory regression tests.

### Minimal negative fixtures

1. Serialized `"texture_filter": "cubic"` fails enum validation.
2. `shading="unlit_rgba"` with `"texture_filter": "linear"` produces `meshvisual_texture_filter_inapplicable`.
3. A valid LINEAR record sent to a nearest-only renderer produces `texture2d_sampler_unsupported`; the corresponding NEAREST record still renders.
4. The producer rejects an invalid filter string and rejects `texture_filter="linear"` without both `texture` and `uvs`.
5. Producer arguments for repeat wrapping, mipmaps, independent min/mag filters, and sampler objects remain rejected.
6. Matplotlib continues rejecting both NEAREST and LINEAR Texture2D meshes and advertises neither texture capability.

Before Datoviz advertises `meshvisual.texture_filter.linear.v1`, a real, non-mocked offscreen run must prove:

* successful public field-slot configuration for LINEAR;
* matching minification and magnification configuration;
* correct orientation, interpolation, clamp, color multiplication, and alpha within `2/255`;
* different filters on two visuals sharing one texture;
* no regression in all existing NEAREST fixtures.

A symbol check, successful compilation, or mocked API call is insufficient.

## 8. Deferred

The following remain explicitly outside this extension:

* independent minification and magnification filters;
* repeat, mirrored-repeat, and border-color wrapping;
* mipmaps, mip-level selection, LOD, and LOD bias;
* anisotropic filtering;
* public sampler resources or sampler identifiers;
* texture mutation, replacement, or streaming semantics;
* sRGB decoding, gamma correction, ICC handling, and display color management;
* perspective-correct UV interpolation, unless already defined independently by the current mesh contract;
* additional texture formats;
* textured Lambert, Phong, PBR, or other lit materials;
* applying this enum to unrelated image, label, volume, or future texture slots.

These exclusions preserve the narrow scope requested by P036. 

## 9. Implementation Plan

1. **Archive and approve the decision**

   * Commit this response as `.agent/consultations/P036-response.md`.
   * Review it against ADR-0029 and `spec/visuals/mesh_texture2d_unlit_s050.md`.
   * Acceptance: ownership, serialization, capability, and diagnostic choices have no unresolved conflict.
   * Stop condition: any conflict that would require a sampler resource, resource-owned sampling, or broader color semantics must return to ADR review before public code changes. 

2. **Add the protocol enum, field, and validation**

   * Add `TextureFilter`.
   * Append `MeshVisual.texture_filter`.
   * Implement missing-field defaulting, canonical default omission, applicability validation, and the new diagnostic.
   * Acceptance: old payloads decode and serialize unchanged; valid LINEAR payloads round-trip; invalid combinations fail deterministically.
   * Stop condition: source compatibility or default decoding cannot be preserved.

3. **Add the reference rule and backend-neutral fixtures**

   * Implement a small test-only CPU reference sampler using the formula in section 3.
   * Add positive and negative fixture records with exact expected values.
   * Acceptance: expected values are independent of any renderer and distinguish LINEAR from NEAREST by substantially more than the tolerance.
   * Stop condition: fixture results depend on unspecified perspective interpolation, blending, or rasterization boundaries.

4. **Extend the VisPy2 producer**

   * Add only `texture_filter`.
   * Lower it to protocol state and add producer validation and capability tests.
   * Acceptance: default calls emit the existing NEAREST representation; LINEAR emits the new field; old rejected sampler arguments remain rejected.
   * Stop condition: implementation would require additional public sampler arguments or backend-specific names.

5. **Implement the Datoviz mapping**

   * Configure the `"texture"` visual field with matching NEAREST/NEAREST or LINEAR/LINEAR values.
   * Retain the current upload role, `v` adaptation, clamp, no-mipmap behavior, and unlit material.
   * Acceptance: two visuals sharing one uploaded resource can use different filters.
   * Stop condition: the public Datoviz API cannot guarantee per-visual-slot state, clamp-to-edge, matching filters, or no mipmaps.

6. **Run conformance and enable capability advertisement**

   * Run the real offscreen fixtures and the full existing S050 suite.
   * Keep Matplotlib behavior and capability sets unchanged.
   * Advertise `meshvisual.texture_filter.linear.v1` only after all runtime checks pass.
   * Acceptance: every channel is within `2/255`, all nearest regressions pass, and capability negotiation produces the required unsupported diagnostic.
   * Stop condition: any runtime mismatch; leave the capability absent rather than loosening semantics or silently falling back.

## 10. Final Recommendation

```python
from dataclasses import dataclass
from enum import Enum


class TextureFilter(str, Enum):
    NEAREST = "nearest"
    LINEAR = "linear"


@dataclass(frozen=True, slots=True)
class MeshVisual:
    # Existing fields remain unchanged and in their existing order.
    # Append this as the final defaulted field for source compatibility.
    texture_filter: TextureFilter = TextureFilter.NEAREST
```

Normative invariants:

```python
# Wire decoding:
#   missing "texture_filter" == TextureFilter.NEAREST
#   "nearest"                == TextureFilter.NEAREST
#   "linear"                 == TextureFilter.LINEAR
#
# Canonical encoding:
#   omit the field for NEAREST
#   emit "texture_filter": "linear" for LINEAR
#
# Applicability:
if (
    visual.shading is not MeshShading.TEXTURE2D_UNLIT
    and visual.texture_filter is not TextureFilter.NEAREST
):
    raise ProtocolValidationError("meshvisual_texture_filter_inapplicable")

# Fixed sampler profile:
#   minification = visual.texture_filter
#   magnification = visual.texture_filter
#   wrap_u = clamp_to_edge
#   wrap_v = clamp_to_edge
#   mipmaps = none
#   lod = base level only
```

Capability rule:

```text
meshvisual.material.texture2d_unlit.v1
    guarantees the existing NEAREST profile

meshvisual.texture_filter.linear.v1
    additionally guarantees the normative LINEAR profile
    and requires:
        texture2d.rgba8.v1
        meshvisual.uv.vertex2d.v1
        meshvisual.material.texture2d_unlit.v1
```
