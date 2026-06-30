# S039 Flat Lambert Normals Decisions

Status: accepted by M171 from P024 response.

## Accepted

- S039 accepts `flat_lambert` only as a narrow, capability-gated diffuse mode for opaque DATA-space
  3D `MeshVisual` triangle meshes.
- Canonical material selectors are `shading="unlit_rgba"` and `shading="flat_lambert"`.
- S039 accepts face normals only: `normal_mode="face"` plus either explicit `(F,3)` normals or
  deterministic `normal_generation="face_flat"`.
- Generated normals use `cross(p1 - p0, p2 - p0)` in DATA coordinates and fail on degenerate or
  non-finite triangles.
- S039 accepts scalar `View3D.ambient_light_intensity` and one optional DATA-space
  `DirectionalLight3D`.
- Direction vectors are from shaded point toward the light.
- Output is `base.rgb * clamp(A + D, 0, 1)` with alpha passthrough.
- Non-opaque 3D mesh alpha remains non-strict.

## Deferred

- `MeshMaterial3D` and material resources.
- Vertex normals and smooth Lambert.
- Phong/specular/shininess and view-vector lighting.
- Multiple lights, colored lights, point/spot lights, attenuation, and scene graphs.
- Textures, UVs, samplers, normal maps, and texture/color combination.
- Lambert on NDC meshes.
- Backend-native material/shader/draw-state names as public API.

## Source

`.agent/consultations/P024-response.md` converted into ADR-0026 and
`spec/visuals/mesh_flat_lambert_s039.md`.
