# M121 - S030 GSP Datoviz guide review-path wiring

## Stage

S030 - Datoviz Guide Axis Proof

## Status

Draft.

## Summary

Wire the GSP Datoviz visual review path for guide/View2D rows only if M120 proves the required
Datoviz native-axis behavior.

## Scope

- `AxisGuide` and `PanelTextGuide` review-pack rendering for Datoviz.
- S029/S030 guide rows only.

## Deliverables

- Adapter wiring with structured unsupported diagnostics for any unproven guide semantics.
- Focused tests for explicit ticks, reversed domains, grid, labels, title placement, and query
  unsupported status.
- Regenerated guide review artifacts if behavior is supported.

## Stop Condition

Stop if Datoviz cannot express exact explicit ticks/labels, reversed-domain axis placement, or panel
title layout without approximation.
