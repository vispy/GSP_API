# M118 - S029 Datoviz guide/View2D unsupported closure

## Stage

S029 - Backend Capability Matrix and Visual Review Pack

## Status

Ready.

## Summary

Close the S029 Datoviz guide/View2D gap by deciding whether current guide rows stay unsupported,
become adapted, or need an upstream Datoviz handoff before promotion.

## Scope

Currently unsupported Datoviz rows:

- `guide/view2d_auto_grid`
- `guide/view2d_reversed_explicit`

## Deliverables

- Unsupported/adapted/strict decision note for Datoviz guide rows.
- Updated capability matrix policy if status changes.
- Upstream Datoviz handoff if missing API or runtime behavior blocks support.
- Regenerated S029 review pack if policy changes.

## Acceptance

- Axis guide, panel title, grid, explicit tick labels, reversed View2D, and guide query semantics are
  explicitly classified.
- No guide row is promoted without exact tick/label/grid evidence.

## Stop Condition

Stop if guide promotion would require unverified Datoviz axis semantics or silent approximation of
tick labels, grid placement, reversed domains, titles, or query payloads.

