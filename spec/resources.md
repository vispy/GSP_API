# GSP Resources - Draft

Resource kinds:

- buffer;
- texture;
- sampled field;
- virtual data source;
- parameter block;
- external/live resource handle.

A buffer resource should eventually carry:

- id;
- dtype;
- shape;
- byte length;
- usage;
- mutability;
- locality;
- update ranges;
- optional external source.

Open v0.1 question: whether to support arbitrary strides immediately or require contiguous buffers first.

M002 decision: the initial `BufferResource` model requires contiguous buffers. Strided views may be represented by `AttributeSource.stride_bytes`, but non-contiguous resource ownership is deferred until a later resource mission.

M011 decision: virtual data sources are not ordinary buffers. `TiledImageSource` describes logical
source data and tile materialization separately from eager `BufferResource` bytes. The local proof
returns direct NumPy arrays from `TileResult` and `ViewportMosaicResult` without mandatory
serialization.

## S050 Texture2D value resources

S050 accepts a narrow `Texture2D` value resource for `MeshVisual.shading="texture2d_unlit"`.

Accepted shape:

| Field | Type | Semantics |
|---|---|---|
| `id` | protocol id string | Unique document-local resource id within one resolved payload. |
| `format` | `"rgba8"` | Only 8-bit straight-alpha RGBA is accepted. |
| `image` | `uint8` array `(H,W,4)` | Non-empty image. `image[0]` is the top row. Channels normalize as `byte / 255.0`. |

`Texture2D` is immutable protocol data, not a backend handle or lifecycle object. S050 does not
accept external paths, URIs, streaming updates, subimage uploads, mipmaps, public sampler objects,
compressed textures, float textures, RGB/grayscale/depth textures, or color-profile metadata.

The accepted texture/UV/material semantics live in
`spec/visuals/mesh_texture2d_unlit_s050.md`.
