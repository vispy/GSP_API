# M166 - S037 Datoviz static View3D mesh binding

## Stage

S037 - Legacy 3D Reuse, Datoviz View3D Binding, and Public 3D Interaction

## Status

Draft, pending M165 evidence.

## Summary

Implement the Datoviz retained `(N, 3)` `MeshVisual` path only if M165 proves a safe public
`View3D` lowering path.

## Deliverables

- Private `DatovizView3DAdapter` or equivalent lowering layer.
- DATA and NDC3 lowering paths.
- Color/index upload and depth-mode mapping.
- Capability gates and diagnostics.
- Focused tests for unsupported binding, missing `View3D`, transform rejection, alpha rejection,
  DATA projection, NDC3 interpretation, and depth evidence.

## Acceptance

- Datoviz renders accepted `(N, 3)` examples without z flattening before claiming support.
- Unsupported environments keep structured `mesh3d_coordinate_space_unsupported` diagnostics.

## Stop Condition

Stop if retained Datoviz rendering cannot prove public GSP `View3D` semantics.
