# M150 - S035 Matplotlib programmatic navigation reference

## Stage

S035 - Retained View2D Navigation and Pan/Zoom

## Status

Ready.

## Summary

Implement a strict reference path for programmatic `View2D` navigation against Matplotlib render and
query behavior.

## Deliverables

- Programmatic navigation action application to Matplotlib protocol scenes.
- Render/query results carrying matching view and layout snapshot identifiers.
- Focused tests for navigation/render/query coherence.
- Explicit unsupported posture for live GUI input if not implemented in this mission.

## Stop Condition

Stop before adding broad GUI event semantics.
