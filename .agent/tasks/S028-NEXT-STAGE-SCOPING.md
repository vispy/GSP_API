# S028 next stage scoping - Guide and View2D Integration

## Status

S028 is ready as the next bounded planning stage after completed S027 Transform, View, Camera, and
Navigation Semantics.

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
| M105 | ready | Audit guide/View2D authority, define S028 implementation batch, and stop on conflicts. |
