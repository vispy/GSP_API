# M104 - S027 QA fixtures and closeout

## Stage

S027 - Transform, View, Camera, and Navigation Semantics

## Status

Completed.

## Summary

Add S027 visual/query QA coverage, close remaining documentation/status gaps, and decide whether the
raw `ANSWER` input can be removed after its contents are fully integrated.

## Deliverables

- Deterministic S027 visual QA or example coverage for affine transform and View2D cases.
- Query fixture coverage for transform inverse payloads.
- Final S027 spec/status closeout, including explicit deferred behavior.
- Remove the root `ANSWER` file only if all relevant content has been integrated into tracked
  code/docs/status.

## Acceptance

- S027 implementation, tests, and docs align with `spec/transforms.md`.
- Mission Control marks S027 complete only after QA/closeout artifacts are present.
- `ANSWER` is deleted only after confirming no unintegrated P012 content remains.

## Stop Condition

Stop if QA closeout reveals a contradiction between ADR/spec, Matplotlib reference behavior,
Datoviz gates, or VisPy2 API.

## Result

- Added S027 visual QA suite cases for inline/named affine equivalence, reversed-limit `View2D`
  DATA/NDC overlay behavior, and cross-family affine plus `View2D` coverage.
- Extended visual QA scene artifacts to serialize transform resources, inline/ref transform
  bindings, and `View2D` state.
- Added focused query fixture coverage for `gsp.transform-query@0.1` inverse payloads.
- Closed S027 without opening a new stage. Public 3D camera/projection/controller, transform graph,
  nonlinear view, equal-aspect layout, image affine, depth, and virtual-source transform semantics
  remain explicitly deferred by ADR-0019 and `spec/transforms.md`.
- Audited the root `ANSWER` file against tracked ADR/spec/status content before deletion.
