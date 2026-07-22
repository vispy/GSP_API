# M267 - S063 interaction contract and failing regression baseline

## Stage

S063 - Live View2D Interaction Parity And Regression Safety

## Status

Draft; requires explicit owner approval.

## Summary

Convert the manually observed Matplotlib and Datoviz interaction failures into deterministic tests
before changing production code. Audit existing navigation authority and record which current tests
encode the static DATA-to-axes lowering that must change deliberately.

## Acceptance

- A Matplotlib test proves DATA artists currently fail to follow a native limit change.
- A companion test proves NDC overlays must remain fixed.
- Tests require canonical `View2D` synchronization and callback cleanup.
- Datoviz session tests prove the canonical live controller is currently not wired.
- Cross-backend action expectations freeze equal canonical range results.
- Baseline suite totals and current Datoviz provenance are recorded.

## Stop conditions

Stop if the failure cannot be reproduced, existing authority conflicts, or the necessary fix would
require a new public protocol/session contract.
