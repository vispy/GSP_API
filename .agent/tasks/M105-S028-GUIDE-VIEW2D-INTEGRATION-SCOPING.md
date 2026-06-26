# M105-S028 - Guide/View2D integration scoping

## Mission

M105

## Goal

Scope S028 around semantic guide behavior now that `View2D` is accepted, and prepare the next
implementation mission batch.

## Status

Completed.

## Deliverables

- Audit existing guide/tick/grid/query specs and tests against `View2D`.
- Decide whether S028 needs a focused spec/ADR update before implementation.
- Draft next missions for Matplotlib guide rendering/query, VisPy2 guide API updates, visual QA,
  and any Datoviz capability/unsupported reporting needed for guide semantics.
- Record explicit deferred behavior.

## Acceptance

- `tools/agentctl next` lists M105 as the recommended next mission.
- S028 remains bounded to semantic guides consuming deterministic `View2D` state.
- Stop conditions are explicit before any worker launch.

## Stop Conditions

- Stop on unresolved conflict between guide specs and `spec/transforms.md`.
- Stop if scope expands into public 3D camera/projection/controller, nonlinear transforms,
  equal-aspect layout, guide collision/layout solving, or live navigation event semantics.

## Result

- No ChatGPT Pro consultation is needed for initial S028 implementation planning.
- S028 should focus on making guides, ticks, grids, guide queries, and readouts consume the same
  deterministic `View2D` snapshot as data visuals.
- Reversed `View2D` limits are the concrete gap: `View2D` accepts them, while current tick resolver
  behavior and tests still reject reversed ranges.
- Next mission is M106, a local spec reconciliation task before worker implementation.
