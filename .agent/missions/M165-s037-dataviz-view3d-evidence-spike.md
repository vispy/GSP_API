# M165 - S037 Datoviz View3D evidence spike

## Stage

S037 - Legacy 3D Reuse, Datoviz View3D Binding, and Public 3D Interaction

## Status

Draft, pending M163.

## Summary

Determine whether the active Datoviz v0.4 bindings can privately lower public GSP `View3D`
semantics for retained `(N, 3)` `MeshVisual` rendering.

## Deliverables

- Binding/header evidence for public View3D/camera-equivalent APIs.
- Runtime probe or structured unsupported report.
- Minimal retained 3D triangle fixture plan for DATA, NDC3, and depth evidence.
- Capability recommendation for Datoviz 3D support.

## Acceptance

- Either evidence passes and M166 can proceed, or current unsupported diagnostics remain.
- No public Datoviz camera, controller, draw-state, or material names leak into GSP API.

## Stop Condition

Stop if the only path depends on private ABI details, unavailable symbols, silent z flattening, or
unverified coordinate/depth semantics.
