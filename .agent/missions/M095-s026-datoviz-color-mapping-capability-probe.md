# M095 - S026 Datoviz color mapping capability probe

## Stage

S026 - Color Mapping, Colorbars, and Scalar Data Semantics

## Status

Completed.

## Summary

Gather Datoviz v0.4 evidence for accepted S026 color mapping/colorbar/scalar readback behavior.

## Planned Deliverables

- Completed: Capability probe updates.
- Completed: Structured unsupported diagnostics or implementation recommendations.

## Outcome

The Datoviz v0.4 probe now records S026 color mapping symbols and capability
gates. Local sibling source contains evidence for scales, colormaps, scalar
sampled fields, visual scale binding, colorbars, and query APIs. The probe now
imports the sibling `../datoviz` checkout automatically, and runtime bindings
expose the accepted S026 image/point/colorbar/query implementation candidates.
Marker scalar fill and mesh face scalar remain capability-gated until native
contracts or explicit CPU-mapped RGBA adaptations are verified.

## Acceptance

- M091 baseline exists.
- Evidence is recorded without freezing backend-private names as protocol.

## Stop Condition

Stop if probing would modify external repos or credentials.
