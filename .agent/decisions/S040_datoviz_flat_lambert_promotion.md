# S040 Datoviz Flat Lambert Promotion Decisions

Status: accepted by M177 from P025 response.

## Accepted

- Datoviz may promote strict S039 `flat_lambert` only through CPU-resolved exact per-face colors.
- Native Datoviz lighting/material APIs are not accepted as S040 strict evidence.
- The adapter must validate S039 through protocol validation before Datoviz upload.
- Face normals must be resolved by protocol code before upload, including deterministic
  `face_flat` generation.
- Lambert colors must be resolved in protocol/backend-neutral code:
  `rgb = base.rgb * clamp(A + D, 0, 1)` and `a = base.a`.
- The Datoviz upload must preserve one constant RGBA per canonical face. Triangle-expanded upload
  with repeated per-face colors is the preferred strict route.
- Native lighting must stay disabled, unused, or proven inert on the CPU-resolved route.
- Non-opaque Datoviz 3D mesh alpha remains non-strict and must report `mesh3d_alpha_not_strict`.
- `meshvisual.material.flat_lambert.v1` may be advertised only after positive and negative fixtures
  prove the CPU-resolved path and all View3D/depth/unlit prerequisites.

## Deferred

- Native Datoviz lighting/material strict promotion.
- Hybrid CPU color plus native lighting.
- Vertex normals, smooth Lambert, Phong/specular, textures, UVs, samplers, multiple lights, and
  material resources.
- Any public exposure of Datoviz-native material, light, shader, draw-state, or controller names.

## Implementation Direction

M178 should implement the CPU-resolved Datoviz route:

1. Validate `flat_lambert` using accepted S039 protocol helpers.
2. Resolve face normals and face RGBA values before upload.
3. Expand triangles when needed so each uploaded triangle has constant per-face RGBA.
4. Upload through the existing C-shaped Datoviz mesh path with depth testing preserved.
5. Promote Datoviz S039 capabilities only behind fixture-backed prerequisites.

## Source

`.agent/consultations/P025-response.md` converted into ADR-0027 and S040 backend-spec updates.
