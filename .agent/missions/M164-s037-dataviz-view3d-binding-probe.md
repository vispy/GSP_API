# M164 - S037 Datoviz View3D binding probe

## Stage

S037 - Legacy 3D Reuse, Datoviz View3D Binding, and Public 3D Interaction

## Status

Draft, pending M162.

## Summary

Probe whether installed Datoviz v0.4 bindings expose a public, stable enough camera/View3D path for
strict or adapted `(N, 3)` `MeshVisual` support.

## Candidate Deliverables

- Binding/header evidence for camera/view APIs.
- Runtime smoke or structured unsupported report.
- Capability matrix update for Datoviz `View3D` mesh support.

## Stop Condition

Stop if the only available path depends on private ABI details, unavailable symbols, or unverified
coordinate/camera semantics.
