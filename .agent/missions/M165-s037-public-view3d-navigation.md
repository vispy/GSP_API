# M165 - S037 public View3D navigation

## Stage

S037 - Legacy 3D Reuse, Datoviz View3D Binding, and Public 3D Interaction

## Status

Draft, pending M162.

## Summary

Implement public `View3D` navigation only after the accepted P021 decision defines the contract.

## Candidate Deliverables

- Protocol navigation dataclasses or controller contract.
- Matplotlib reference interaction if accepted.
- Query/snapshot freshness semantics.
- Tests for pan/orbit/zoom or any accepted subset.

## Stop Condition

Stop if the accepted design requires perspective, backend-native controller exposure, or a scene
graph before those are specified.
