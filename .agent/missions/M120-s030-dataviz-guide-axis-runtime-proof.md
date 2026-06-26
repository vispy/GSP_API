# M120 - S030 Datoviz guide-axis runtime proof

## Stage

S030 - Datoviz Guide Axis Proof

## Status

Ready.

## Summary

Probe and render Datoviz native panel-axis behavior for the two S029 guide/View2D cases before any
GSP capability promotion.

## Scope

- `guide/view2d_auto_grid`
- `guide/view2d_reversed_explicit`

## Deliverables

- Datoviz runtime probe or rendered artifacts for native axes under normal and reversed `View2D`.
- Evidence for backend auto ticks, explicit tick values/labels, grid visibility/placement, axis
  labels, and panel title placement.
- Updated handoff if Datoviz lacks exact API/runtime behavior.

## Acceptance

- No GSP matrix row is promoted in this mission.
- Each required guide behavior is classified as proven, adapted, unsupported, or blocked.
- Guide/all-rendered query remains unsupported unless Datoviz guide picking/query is explicitly
  proven.

## Stop Condition

Stop if promotion would require silently approximating explicit ticks, reversed domains, title
layout, grid placement, or guide query behavior.
