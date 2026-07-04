# ADR-0029 - MeshVisual Unlit Texture2D Material

## Status

Accepted

## Context

S038 accepted only implicit `unlit_rgba` material semantics for existing `MeshVisual` RGBA colors.
S039 accepted a narrow flat Lambert extension with face normals and scalar white lights. Both stages
reserved textures, UVs, samplers, and textured materials for a later architecture decision.

P031 reviewed the next material/API step after S050 evidence and recommended the smallest remaining
material expansion: immutable RGBA8 `Texture2D` resources, per-vertex UVs, and one unlit textured
mesh material. This ADR converts that recommendation into protocol authority before implementation.

## Decision

GSP accepts a minimal unlit Texture2D material for `MeshVisual`.

Accepted public concepts:

- immutable document-local `Texture2D` value resources;
- `Texture2D.format="rgba8"` only;
- `Texture2D.image` as a contiguous `uint8` array shaped `(H, W, 4)`;
- canonical `MeshVisual.shading="texture2d_unlit"`;
- `MeshVisual.texture2d_id`;
- `MeshVisual.uv_mode="vertex"`;
- `MeshVisual.uvs` as finite float `(N, 2)` values indexed by existing mesh vertices;
- fixed nearest/clamp/base-level sampling;
- multiplicative unlit color and alpha composition.

The new material is mutually exclusive with `flat_lambert`. It does not add public material objects,
public sampler objects, backend texture handles, Datoviz slots, Matplotlib artists, model loading,
smooth normals, Phong/specular terms, culling semantics, transparency sorting, or expanded query
payloads.

## Texture And UV Semantics

`Texture2D` is a protocol value resource, not a backend handle. A texture id is unique within one
resolved payload and may be referenced by multiple visuals. v1 does not define mutation, streaming,
subimage updates, external paths, URIs, file loading, or resource lifetimes beyond the payload.

Only `rgba8` is accepted. `Texture2D.image` must be `uint8` with shape `(H, W, 4)` and non-zero
dimensions. `image[0, :, :]` is the top image row. Sampled channel values are normalized by
`byte / 255.0`.

UV coordinates use:

- `u` increases left to right;
- `v` increases bottom to top;
- `(0, 0)` is the bottom-left texture edge;
- `(1, 1)` is the top-right texture edge.

For a 2x2 texture, texel centers are approximately `(0.25, 0.25)`, `(0.75, 0.25)`,
`(0.25, 0.75)`, and `(0.75, 0.75)`. Since `image[0]` is the top row, `(0.25, 0.75)` samples the
top-left texel.

UVs are per vertex. `uvs.shape == (N, 2)` and `uvs[i]` belongs to `positions[i]`; `faces` index both
positions and UVs. Seams require duplicated positions with distinct UV values. v1 does not accept
separate UV indices, per-corner UVs, face-varying UVs, or generated UVs.

## Sampling And Color Rule

The v1 sampler is fixed:

```text
filter = nearest
wrap_u = clamp_to_edge
wrap_v = clamp_to_edge
mipmap = none
lod = base level only
```

Backends must not expose or accept public linear filtering, repeat/mirror wrap, border colors,
anisotropy, mipmaps, LOD bias, backend sampler names, or color-management controls in this stage.

The material formula is:

```text
tex = sample_nearest_clamp(texture, interpolated_uv)
base = resolve_mesh_rgba(MeshVisual.color, MeshVisual.color_mode)

output.rgb = clamp(base.rgb * tex.rgb, 0.0, 1.0)
output.a   = clamp(base.a * tex.a, 0.0, 1.0)
```

The material is unlit. Normals, lights, camera position, view direction, depth value, generated
backend attributes, and backend-native material state must not affect color.

`rgba8` is treated as unmanaged numeric RGBA code values. This ADR does not define sRGB decode,
linear-light conversion, ICC profiles, gamma-correct filtering, display color management, or
perceptual blending.

## Alpha And Depth

Strict opaque 3D conformance for textured meshes requires base alpha `1.0` and every texture alpha
byte equal to `255`. Otherwise the material can still define pre-composition RGBA, but final 3D
compositing is non-strict and must use `mesh3d_alpha_not_strict`.

This ADR does not change existing depth, draw order, or culling rules. Combining textured meshes
with `meshvisual.positions3d.opaque_depth.v1` is valid only when the backend already supports the
retained DATA-space View3D opaque-depth path and the conservative opacity requirement is satisfied.

## Capability Boundary

Accepted in this ADR:

```text
texture2d.rgba8.v1
meshvisual.uv.vertex2d.v1
meshvisual.material.texture2d_unlit.v1
vispy2.producer.mesh.texture2d_unlit.v1
```

`meshvisual.material.texture2d_unlit.v1` requires both `texture2d.rgba8.v1` and
`meshvisual.uv.vertex2d.v1`. It does not imply Lambert texturing, Phong, smooth normals, normal
maps, texture arrays, alpha sorting, culling, model loading, or mesh picking payload expansion.

## Backend Expectations

Matplotlib must not advertise `meshvisual.material.texture2d_unlit.v1` through its current
CPU-projected 3D mesh path. Face coloring is not texture mapping. Matplotlib may reject textured
meshes with `meshvisual_material_texture2d_unlit_unsupported` until a fixture-backed CPU textured
triangle rasterizer exists.

Datoviz may advertise the texture capabilities only through public APIs that expose canonical RGBA8
texture data, canonical per-vertex UVs, fixed nearest/clamp/base-level sampling, and the accepted
image-origin/color rules. Private Vulkan state, private shader slots, private mesh ids, and
backend-native texture objects are not public GSP semantics.

VisPy2 may add only a thin producer convenience that lowers to canonical GSP fields and resources.
Producer capability is separate from renderer capability.

## Deferred

Deferred after this ADR:

- public material objects;
- textured Lambert, smooth Lambert, vertex normals, normal interpolation, Phong, Blinn-Phong,
  specular color, shininess, PBR, normal maps, bump maps, tangent frames, and displacement maps;
- multiple textures, texture arrays, 3D textures, cube maps, atlases, external image files,
  compressed textures, float textures, RGB textures, grayscale textures, and depth textures;
- public sampler objects, linear filtering, repeat/mirror wrap, border colors, mipmaps, anisotropy,
  and LOD controls;
- strict alpha/transparency semantics, transparency sorting, alpha test/discard, culling expansion,
  and order-independent transparency;
- model loading, OBJ/glTF import, instancing, mesh-local transforms, scene graphs, and hierarchical
  nodes;
- Datoviz slots, Vulkan state, Matplotlib artists, shader names, draw calls, and backend-native
  controllers;
- expanded 3D query payloads, private backend face ids, and mesh triangle picking extensions;
- perspective-correct texturing and perspective camera texturing.

## Consequences

The next implementation missions may add protocol dataclasses/enums/validation, fixtures, backend
capability gates, and a thin VisPy2 producer helper for the accepted fields. They must not implement
broader materials, samplers, alpha/culling semantics, query expansion, or backend-native API surfaces
without separate accepted decisions.

## Source

`.agent/consultations/P031-response.md` converted into this ADR and
`spec/visuals/mesh_texture2d_unlit_s050.md`.
