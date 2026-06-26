# M116 - S029 Datoviz mesh promotion audit

## Stage

S029 - Backend Capability Matrix and Visual Review Pack

## Status

Ready.

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

