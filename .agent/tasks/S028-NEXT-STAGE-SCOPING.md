# S028 next stage scoping - Guide and View2D Integration

## Status

S028 is in progress after completed S027 Transform, View, Camera, and Navigation Semantics.

## Selected direction

Guide/View2D integration should reconcile existing semantic guide behavior with accepted
deterministic `View2D` semantics:

- axis guides, ticks, tick labels, grids, and panel labels consume `View2D` limits;
- deterministic tick/grid/readout behavior must follow explicit and auto tick policy under normal
  and reversed axes;
- guide queries and data queries should report coordinates tied to the same `View2D` snapshot;
- Matplotlib remains the strict reference path;
- VisPy2 producer APIs should emit GSP protocol records only;
- Datoviz behavior should be capability-gated or reported as structured unsupported if semantics
  cannot be verified.

## Consultation policy

No ChatGPT Pro consultation is required for the initial S028 scoping pass. This stage is a
reconciliation of already accepted guide and `View2D` semantics.

Create a ChatGPT Pro packet only if scoping reveals a durable architecture question, such as
conflicting guide authority documents, public guide layout/collision semantics, equal-aspect layout,
nonlinear axes, or expansion into public 3D camera/projection/controller behavior.

## Immediate next missions

| Mission | State | Purpose |
|---|---|---|
| M105 | completed | Audited guide/View2D authority, defined S028 implementation batch, and found no architecture blocker. |
| M106 | ready | Reconcile specs around guide/tick/query consumption of `View2D`, including reversed axes. |
| M107 | draft | Implement deterministic reversed-`View2D` tick and Matplotlib guide rendering behavior after M106. |
| M108 | draft | Implement guide query/readout parity for the same `View2D` snapshot after M106/M107. |
| M109 | draft | Add visual QA and VisPy2 coverage for guide/View2D behavior. |
| M110 | draft | Add Datoviz guide capability/unsupported reporting and close S028. |
