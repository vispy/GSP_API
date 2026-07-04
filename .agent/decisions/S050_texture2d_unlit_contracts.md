# S050 Texture2D Unlit Mesh Contracts

Status: accepted from P031 response.

Authority:

- `adr/ADR-0029-mesh-texture2d-unlit.md`
- `spec/visuals/mesh_texture2d_unlit_s050.md`
- `.agent/consultations/P031-response.md`

## Decision

The next material stage is unlit `Texture2D` plus per-vertex UVs for `MeshVisual`.

Accepted capabilities:

```text
texture2d.rgba8.v1
meshvisual.uv.vertex2d.v1
meshvisual.material.texture2d_unlit.v1
vispy2.producer.mesh.texture2d_unlit.v1
```

## Implementation Gate

Do not advertise renderer support until fixtures prove the accepted texture resource, UV,
sampling, alpha, and color-multiplication semantics. Matplotlib remains unsupported unless a CPU
textured-triangle rasterizer is added. Datoviz requires public API evidence for canonical RGBA8
texture upload, per-vertex UV binding, nearest/clamp/no-mipmap sampling, and compatible origin/color
behavior.

## Still Deferred

Alpha/culling semantics, strict transparency, smooth normals, Phong/specular/PBR, public material
objects, public samplers, model loading, mesh-local transforms, scene graphs, perspective-correct
texturing, and expanded 3D query payloads remain separate consultation or architecture tracks.
