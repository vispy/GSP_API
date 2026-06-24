# ADR-0017 - MeshVisual v1 triangular mesh only

## Status

Accepted

## Context

S025 follows the accepted S023/S024 visual-family baseline. Mesh support risks freezing a broad 3D
scene graph, material system, geometry-resource model, texture pipeline, or Datoviz-specific mesh API
if the public protocol is not bounded first.

## Decision

S025 accepts public `MeshVisual` as the only mesh/3D visual family for v1.

- `MeshVisual` owns inline indexed triangle geometry: `positions` and `faces`.
- `positions` are finite float32/float64 arrays with shape `(N, 2)` or `(N, 3)`.
- `faces` are integer arrays with shape `(M, 3)` and valid indices into `positions`.
- Public v1 supports triangles only; quads, polygons, strips, fans, surfaces, and volumes are deferred.
- `coordinate_space` uses existing `CoordinateSpace.NDC` or `CoordinateSpace.DATA`.
- Required color modes are `uniform` RGBA and `face` RGBA. `vertex` RGBA is optional and
  capability-gated.
- Strict v1 shading is `flat`: colors are used directly without public light/material semantics.
- `normals`, `normal_mode`, explicit `normal_generation=face_flat`, and `shading=lambert` are
  optional/capability-gated, not strict conformance.
- Depth and culling are conservative controls: `depth_test`, `depth_write`, and `face_culling`.
  Unsupported explicit requests require structured diagnostics.
- 2D mesh rendering is the strict Matplotlib reference/conformance path. 3D mesh rendering is
  capability-gated and must use existing panel/view camera semantics; `MeshVisual` does not define a
  camera or mesh-local transform.
- Mesh query/readback is face-level when supported: visual id, family, face index, vertex indices,
  panel coordinate, coordinate space, displayed RGBA, and depth when available. Barycentric
  coordinates, hit position, normals, and 3D query are capability-gated.
- Public `GeometryResource`, public `Material`, `SurfaceVisual`, `VolumeVisual`, UVs/textures,
  instancing, external model loading, scalar colormaps/colorbars, wireframe conformance, advanced
  transparency, PBR, lights, shadows, clipping, LOD, and GPU-generated geometry are deferred.
- Datoviz retained mesh APIs are backend implementation evidence only. Public GSP fields must not use
  Datoviz slot names, material structs, geometry loaders, or draw calls.

## Consequences

Workers can implement deterministic validation, 2D Matplotlib reference rendering, strict visual QA,
Datoviz capability probes, and structured unsupported reports without inventing a full 3D engine.
Datoviz may support more mesh features internally, but S025 exposes only the accepted semantic subset
unless later ADRs expand the protocol.
