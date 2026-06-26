# M108-S028 - Guide query/readout View2D parity

## Mission

M108

## Goal

Make guide query and readout behavior consume the same deterministic `View2D` state as rendering.

## Status

Draft.

## Deliverables

- Reversed-axis guide query tests.
- Same-snapshot guide/data scoped-query coverage.
- Clear unsupported diagnostics for unavailable guide query behavior.

## Acceptance

- Focused guide-query and scoped-query tests pass.
- Results do not silently adapt unsupported guide behavior.
