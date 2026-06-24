# S025 MeshVisual Contract Decisions

Status: accepted by M083 from P010 response.

## Accepted

- Public v1 defines `MeshVisual` only.
- Geometry is inline indexed triangles: `positions` `(N,2|3)` and `faces` `(M,3)`.
- Strict conformance is 2D filled triangles in NDC/DATA, flat shaded, opaque, uniform or per-face RGBA.
- Per-vertex color, normals, generated face normals, Lambert shading, 3D rendering, culling, alpha,
  and mesh query beyond the 2D face baseline are capability-gated.
- Mesh query is face-level when supported.
- Matplotlib is strict reference for 2D; Datoviz is flagship GPU backend behind retained-v0.4 mesh
  capability gates.

## Deferred

Geometry resources, public materials/lights, textures/UVs, surface/volume visuals, instancing,
mesh-local transforms, external model loading, scalar colormaps/colorbars, wireframe conformance,
advanced transparency, LOD/chunking, and public Datoviz implementation names.

## Source

`.agent/consultations/P010-response.md` converted into ADR-0017 and `spec/visuals/mesh.md`.
