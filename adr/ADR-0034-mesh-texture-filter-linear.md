# ADR-0034 - Mesh Texture Filter Linear Extension

## Status

Accepted.

## Context

ADR-0029 accepts immutable RGBA8 `Texture2D` resources and an unlit mesh material with a fixed
nearest/clamp/no-mipmap sampler. Datoviz now exposes public sampling state per visual field slot and
supports matching nearest or linear minification/magnification. P036 reviewed whether GSP should
expose that additional choice without introducing a general sampler model.

## Decision

GSP adds `TextureFilter`, with values `nearest` and `linear`, and appends
`MeshVisual.texture_filter: TextureFilter = TextureFilter.NEAREST`. Sampling belongs to the visual's
texture field slot, not the immutable pixel resource, so multiple visuals may sample one
`Texture2D` differently.

Missing and explicit `nearest` values have identical semantics. Canonical encoders omit the default
and emit `"texture_filter": "linear"` only for linear filtering. Linear is valid only with
`shading="texture2d_unlit"`; a non-textured visual requesting it fails with
`meshvisual_texture_filter_inapplicable`.

One enum controls matching minification and magnification. Both filters retain clamp-to-edge in u/v,
no mipmaps, and base-level-only sampling. This ADR does not add sampler resources, independent
min/mag state, configurable wrap, mipmaps/LOD, anisotropy, texture mutation, additional formats,
color management, or textured lighting.

## Linear Sampling Rule

For finite interpolated `(u, v)`, texture width `W`, height `H`, and top-to-bottom array rows:

```text
uc = clamp(u, 0, 1)
vc = clamp(v, 0, 1)
x = W * uc       - 0.5
y = H * (1 - vc) - 0.5
px = floor(x); py = floor(y)
fx = x - px;  fy = y - py
i0 = clamp(px,     0, W - 1); i1 = clamp(px + 1, 0, W - 1)
j0 = clamp(py,     0, H - 1); j1 = clamp(py + 1, 0, H - 1)
```

Normalize straight-alpha RGBA8 channels as `C[j,i] = image[j,i] / 255`, then evaluate:

```text
top    = (1 - fx) * C[j0,i0] + fx * C[j0,i1]
bottom = (1 - fx) * C[j1,i0] + fx * C[j1,i1]
tex    = (1 - fy) * top      + fy * bottom
output.rgb = clamp(base.rgb * tex.rgb, 0, 1)
output.a   = clamp(base.a   * tex.a,   0, 1)
```

Filtering occurs on unmanaged numeric RGBA code values before base-color multiplication. RGB is not
premultiplied by alpha. No sRGB decode, gamma correction, or ICC transform occurs. Conformance
readback permits absolute per-channel error at most `2/255` from the real-valued reference.

## Capabilities

`meshvisual.material.texture2d_unlit.v1` retains its existing nearest guarantee. Linear rendering
requires the additional `meshvisual.texture_filter.linear.v1`, which depends on
`texture2d.rgba8.v1`, `meshvisual.uv.vertex2d.v1`, and the existing material capability.

The producer capability `gsp_vispy2.producer.mesh.texture_filter.linear.v1` is independent of
renderer support and depends on `gsp_vispy2.producer.mesh.texture2d_unlit.v1`.

## Backend And Producer Boundary

Datoviz maps the enum to per-visual mesh `"texture"` field-slot sampling and advertises linear only
after real runtime conformance. Matplotlib remains unsupported for all textured meshes. VisPy2 adds
only `texture_filter="nearest"`; linear without both texture and UVs is invalid.

## Consequences

All existing payloads remain nearest and all existing capability consumers remain valid. Older
nearest-only renderers accept nearest records and diagnose valid linear requests with
`texture2d_sampler_unsupported`; they must never silently downgrade linear to nearest.
