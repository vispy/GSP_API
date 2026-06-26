# M116 - S029 Datoviz mesh promotion audit

## Stage

S029 - Backend Capability Matrix and Visual Review Pack

## Status

Completed.

## Summary

Audit Datoviz mesh rows that currently render in the S029 review pack and decide which exact 2D
rendering scopes can move from `adapted` to `strict`.

## Scope

Rendered Datoviz rows:

- `mesh/single_triangle_uniform_ndc_2d`
- `mesh/indexed_square_uniform_ndc_2d`
- `mesh/indexed_square_per_face_ndc_2d`

## Deliverables

- Per-row mesh promotion notes tied to capability matrix rows.
- Updated capability matrix policy only for exact proven 2D mesh rendering scopes.
- Tests covering promoted strict/adapted metadata.
- Regenerated S029 review pack.

## Acceptance

- Indexed geometry, uniform color, and per-face color are promoted only when exact rendered semantics
  are documented.
- 3D mesh, normals, materials, depth, textures, and mesh query/readback remain unpromoted unless
  separately proven.

## Stop Condition

Stop if strict promotion would require silently approximating indexing, face color, depth, 3D
semantics, or query behavior.

## Completion

Completed on 2026-06-26 in the local Mission Control session.

- Added `.agent/S029_DATOVIZ_MESH_AUDIT.md`.
- Promoted `mesh/single_triangle_uniform_ndc_2d`, `mesh/indexed_square_uniform_ndc_2d`, and
  `mesh/indexed_square_per_face_ndc_2d` to `strict` for rendering only.
- Documented the exact 2D NDC mesh scopes, including Datoviz `z=0` upload, disabled depth testing,
  preserved indexed uniform geometry, and per-face RGBA adaptation by triangle-vertex duplication.
- Preserved `query_supported: false` for all mesh rows.
- Regenerated `artifacts/visual_qa/s029/current-review-pack`.
