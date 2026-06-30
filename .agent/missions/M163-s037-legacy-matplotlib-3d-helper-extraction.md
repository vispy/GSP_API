# M163 - S037 legacy Matplotlib 3D helper extraction

## Stage

S037 - Legacy 3D Reuse, Datoviz View3D Binding, and Public 3D Interaction

## Status

Draft, pending M162.

## Summary

Extract only accepted, spec-compatible legacy Matplotlib 3D helper techniques into the current
protocol renderer path.

## Candidate Deliverables

- Internal projection/depth/normal helper functions with focused unit tests.
- No public API changes unless accepted by M162.
- Adapted renderer behavior kept deterministic for review fixtures.

## Stop Condition

Stop if extraction would import legacy public camera/material/light classes or alter S036 static
`View3D` semantics.
