# MeshVisual Texture2D Unlit Material - S050

Status: accepted S050 protocol boundary.

Semantic purpose: add the smallest backend-neutral texture material after S038 unlit RGBA and S039
flat Lambert, while keeping material objects, sampler objects, model loading, alpha/culling
semantics, and backend-native texture handles out of scope.

## Scope

S050 accepts unlit RGBA8 texture sampling for `MeshVisual` with per-vertex UVs.

In scope:

- immutable document-local `Texture2D` resources;
- `rgba8` pixel data only;
- per-vertex UVs indexed by the existing mesh faces;
- fixed nearest/clamp/no-mipmap sampling;
- multiplicative unlit RGBA output;
- conservative opaque-alpha gate for strict 3D depth conformance.

Out of scope:

- public material objects;
- public sampler objects;
- textured lighting, smooth normals, Phong, specular, normal maps, and PBR;
- texture arrays, external image files, compressed/float/RGB/grayscale/depth textures;
- culling expansion, transparency sorting, alpha test/discard, and OIT;
- model loading, instancing, mesh-local transforms, and scene graphs;
- backend-native texture slots, shader names, draw calls, Matplotlib artists, or Datoviz objects;
- expanded 3D query payloads and mesh-picking extensions.

## Public Schema

| Field/resource | Type | Default | Semantics |
|---|---|---|---|
| `Texture2D.id` | protocol id string | required | Document-local immutable resource id, unique in one resolved payload. |
| `Texture2D.format` | `"rgba8"` | `"rgba8"` | Only 8-bit straight-alpha RGBA is accepted. |
| `Texture2D.image` | `uint8` array `(H,W,4)` | required | Non-empty pixel data. `image[0]` is the top row. Channels normalize as `byte / 255.0`. |
| `MeshVisual.shading` | `"unlit_rgba"` / `"flat_lambert"` / `"texture2d_unlit"` | `"unlit_rgba"` | `texture2d_unlit` selects this material and is mutually exclusive with `flat_lambert`. |
| `MeshVisual.texture2d_id` | `str` or `None` | `None` | Required for `texture2d_unlit`; must reference a declared `Texture2D`. |
| `MeshVisual.uv_mode` | `"none"` / `"vertex"` | `"none"` | `vertex` means one UV pair per mesh vertex. |
| `MeshVisual.uvs` | finite float array `(N,2)` or `None` | `None` | Required for `uv_mode="vertex"` and `texture2d_unlit`; `N == len(positions)`. |

`texture2d_id` must be absent or `None` for strict `unlit_rgba` and `flat_lambert` payloads unless
a later material explicitly consumes it.

## UV Semantics

`u` increases left to right and `v` increases bottom to top. Texture coordinate `(0, 0)` is the
bottom-left texture edge; `(1, 1)` is the top-right texture edge.

Because `Texture2D.image[0]` is the top image row, high `v` samples earlier image rows. For a 2x2
texture, `(0.25, 0.75)` samples the top-left texel and `(0.25, 0.25)` samples the bottom-left texel.

UVs are interpolated affinely across each triangle. This is the accepted v1 behavior for the current
orthographic View3D baseline. Perspective-correct interpolation remains deferred.

Texture seams require duplicate positions with different UV values. Separate UV index buffers,
per-corner UVs, per-face UVs, generated UVs, and face-varying UV topology are unsupported in v1.

## Sampling, Color, And Alpha

The fixed sampler is:

| Parameter | Value |
|---|---|
| minification filter | `nearest` |
| magnification filter | `nearest` |
| `u` wrap | `clamp_to_edge` |
| `v` wrap | `clamp_to_edge` |
| mipmaps | none |
| LOD | base level only |

Let `base` be the resolved S038 mesh RGBA color and `tex` be the sampled normalized RGBA texel:

```text
output.rgb = clamp(base.rgb * tex.rgb, 0.0, 1.0)
output.a   = clamp(base.a * tex.a, 0.0, 1.0)
```

No light, normal, camera, view direction, backend material state, or generated backend attribute may
modify the result. `rgba8` is unmanaged numeric RGBA. This spec defines no sRGB decode,
linear-light conversion, ICC handling, gamma-correct filtering, or display color management.

For strict opaque 3D conformance, `base.a == 1.0` and all texture alpha bytes must be `255`. Any
base alpha below 1 or texture alpha below 255 triggers `mesh3d_alpha_not_strict` for 3D
compositing/depth claims.

## Capabilities

| Capability | Meaning | Requirements |
|---|---|---|
| `texture2d.rgba8.v1` | Renderer/protocol can validate and resolve immutable RGBA8 `Texture2D` resources. | `uint8 (H,W,4)`, non-empty dimensions, no silent coercion or color conversion. |
| `meshvisual.uv.vertex2d.v1` | Renderer/protocol accepts per-vertex UVs indexed by mesh faces. | finite `(N,2)` UVs, no alternate UV topology. |
| `meshvisual.material.texture2d_unlit.v1` | Renderer samples RGBA8 texture with fixed sampler and multiplicative unlit RGBA output. | Requires `texture2d.rgba8.v1` and `meshvisual.uv.vertex2d.v1`. |
| `vispy2.producer.mesh.texture2d_unlit.v1` | VisPy2 can emit canonical textured mesh payloads. | Producer-only; renderers still need renderer capabilities. |

`meshvisual.positions3d.opaque_depth.v1` may combine with textured meshes only for retained
DATA-space View3D paths that already satisfy opaque-depth requirements and only when final alpha is
conservatively opaque.

## Diagnostics

| Diagnostic | Trigger | Required behavior |
|---|---|---|
| `texture2d_invalid_resource` | Missing id, duplicate id, invalid/empty shape, invalid dtype, unsupported format, or wrong channel count. | Reject strict payload; do not coerce. |
| `texture2d_unknown_id` | `MeshVisual.texture2d_id` references no declared texture. | Reject strict payload. |
| `texture2d_resource_limit_exceeded` | Texture dimensions or aggregate texture bytes exceed backend limits. | Fail explicitly; no silent downscaling. |
| `meshvisual_texture_required` | `shading="texture2d_unlit"` without `texture2d_id`. | Reject strict payload. |
| `meshvisual_uv_required` | `texture2d_unlit` without `uv_mode="vertex"` and `uvs`. | Reject strict payload. |
| `meshvisual_uv_shape_mismatch` | `uvs` is not `(N,2)`. | Reject strict payload. |
| `meshvisual_uv_nonfinite` | Any UV is NaN or infinite. | Reject strict payload. |
| `meshvisual_uv_topology_unsupported` | Separate UV indices, per-corner UVs, per-face UVs, or generated UVs requested. | Reject unless a later capability accepts it. |
| `meshvisual_material_texture2d_unlit_unsupported` | Renderer lacks textured mesh material support. | Reject/diagnose; never render as flat color silently. |
| `texture2d_sampler_unsupported` | Linear filtering, repeat wrap, mipmaps, border colors, anisotropy, or sampler state requested. | Reject in v1. |
| `texture2d_colorspace_unsupported` | sRGB decode, ICC, linear-light conversion, or other color management requested. | Reject in v1. |
| `meshvisual_texture_lighting_conflict` | Texture material is combined with Lambert/Phong/material/light semantics intended to affect color. | Reject in v1. |
| `mesh3d_alpha_not_strict` | Textured 3D mesh has base alpha `< 1` or any texture alpha byte `< 255`. | Rendering is non-strict for final 3D compositing/depth claims. |

## Backend Conformance

Matplotlib must not advertise `meshvisual.material.texture2d_unlit.v1` through the current
`PolyCollection`/CPU-projected 3D mesh path. It may reject textured meshes with
`meshvisual_material_texture2d_unlit_unsupported`. A future Matplotlib implementation would need a
fixture-backed CPU textured triangle rasterizer.

Datoviz may advertise `texture2d.rgba8.v1`, `meshvisual.uv.vertex2d.v1`, and
`meshvisual.material.texture2d_unlit.v1` only after public Datoviz APIs prove canonical RGBA8
upload, canonical per-vertex UV binding, nearest/clamp/no-mipmap sampling, compatible image origin,
and unmanaged numeric color behavior. Private Vulkan objects, shader slots, mesh ids, or
backend-native texture handles are not evidence.

VisPy2 may add only a thin producer helper that lowers to accepted GSP fields. It must not expose
backend texture handles, sampler controls, file loading, material classes, shading controls, or
backend-specific keywords.

## VisPy2 Producer API

After protocol validation lands, VisPy2 may extend `Axes.mesh` only as:

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

Rules:

- `texture is None and uvs is None` preserves current mesh behavior exactly;
- both `texture` and `uvs` are required to emit `texture2d_unlit`;
- `texture` must be strict `uint8 (H,W,4)` with no semantic conversion;
- `uvs` must be finite `(N,2)`;
- `color` remains the multiplicative base color;
- supplying exactly one of `texture` or `uvs` is an error;
- no `sampler`, `wrap`, `filter`, `mipmap`, `material`, `normal`, `light`, `shading`,
  `texture_id`, culling/depth-state, or backend-specific keyword is accepted in this stage.

## Fixtures

Positive fixtures before advertising renderer support:

- single NDC triangle with a 2x2 RGBA8 texture, UVs at texel centers, and white base color;
- two-triangle NDC quad with a 4x4 checker texture and clamp-to-edge UVs;
- DATA-space orthographic View3D opaque textured quad;
- overlapping opaque textured DATA-space meshes on backends that already claim strict opaque depth;
- color multiplication swatches for uniform base color times known texels;
- duplicate-position seam fixture;
- clamp fixture with UVs outside `[0, 1]`;
- alpha diagnostic fixture with at least one texture alpha byte below `255`.

Negative fixtures:

- `texture2d_unlit` without `texture2d_id`;
- unknown texture id;
- texture shape other than `(H,W,4)`;
- texture dtype other than `uint8`;
- empty texture dimensions;
- missing, wrong-length, wrong-shape, NaN, or infinite UVs;
- separate UV indices, per-corner UVs, generated UVs, or face-varying UVs;
- requested linear filtering, repeat wrap, mipmaps, sRGB decode, border color, anisotropy, or a
  sampler object;
- texture material combined with Lambert, Phong/specular fields, normal maps, or material/light
  semantics intended to affect texture color;
- unsupported backend receiving a textured mesh;
- non-opaque textured 3D mesh attempting to claim strict opaque-depth conformance.

Manual review artifacts should include a quadrant UV-orientation plate, checkerboard textured quad,
duplicate-vertex seam plate, and color-multiplication swatches.

## Implementation Boundary

Implementation may add protocol dataclasses/enums/validation, conformance fixtures, backend
capability gates, Datoviz public-API evidence probes, Matplotlib unsupported diagnostics, and the
thin VisPy2 producer helper. It must not expand public materials, samplers, culling, alpha sorting,
model loading, query payloads, or backend-native texture surfaces.
