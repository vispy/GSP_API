# M185 - S043 GSP partial Datoviz snapshot adapter

## Stage

S043 - Datoviz Panel Frame, Guide Strictness, And Retained View3D

## Status

Draft.

## Summary

Map available Datoviz panel frame snapshot fields into GSP `ResolvedLayoutSnapshot` while preserving
adapted diagnostics for missing strict guide semantics.

## Deliverables

- Datoviz snapshot binding/facade detection in GSP.
- Mapping from Datoviz panel/plot/grid rects, device scale, view transforms, diagnostics, and
  available guide fields into GSP layout snapshot structures.
- New partial snapshot capability and diagnostics.
- Native grid clipping capability remains independently detectable.
- Focused tests for snapshot id equality on available fields.
- Review-pack diagnostics that distinguish native grid clipping from full guide strictness.

## Acceptance

- GSP does not synthesize strict fields Datoviz cannot report.
- Pixel-unit/device-scale assumptions are explicit.
- Existing adapted guide rows remain adapted until guide query/contribution evidence exists.

## Stop Conditions

- Stop if GSP must invent guide boxes or contribution ids not reported by Datoviz.
- Stop if Datoviz and GSP disagree on logical pixel or device-scale units.
