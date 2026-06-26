# M117 - S029 Datoviz transform promotion audit

## Stage

S029 - Backend Capability Matrix and Visual Review Pack

## Status

Ready.

## Summary

Audit Datoviz transform rows that currently render in the S029 review pack and decide which exact
affine/View2D rendering scopes can move from `adapted` to `strict`.

## Scope

Rendered Datoviz rows:

- `transform/inline_named_equivalence`
- `transform/view2d_data_ndc_overlay`
- `transform/family_affine_view2d`

## Deliverables

- Per-row transform promotion notes tied to capability matrix rows.
- Updated capability matrix policy only for exact proven transform rendering scopes.
- Tests covering promoted strict/adapted metadata.
- Regenerated S029 review pack.

## Acceptance

- Inline affine, named affine, View2D DATA-to-NDC, and reversed-limit behavior are promoted only for
  visual families with evidence.
- Inverse transform query payloads remain unpromoted unless separately proven.

## Stop Condition

Stop if strict promotion would require silently approximating named transforms, reversed View2D
limits, family-specific transform behavior, or query inverses.

