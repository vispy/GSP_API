# M104-S027 - QA fixtures and closeout

## Mission

M104

## Goal

Add S027 QA/fixture coverage and close the stage once transform/view/query inverse behavior is
integrated consistently.

## Status

Completed.

## Deliverables

- Add visual QA or fixture coverage for affine transform and View2D cases.
- Add query fixture coverage for transform inverse payloads.
- Update status/docs/spec index as needed for closeout.
- Audit the root `ANSWER` file against tracked code/docs; delete it only when fully integrated.

## Acceptance

- Full tests pass or known unrelated failures are documented.
- S027 status is accurate and next stage is not opened prematurely.
- No P012 content needed for S027 remains only in `ANSWER`.

## Stop Conditions

- Stop on unresolved spec/implementation conflict.
- Stop if deletion of `ANSWER` would discard unintegrated P012 content.

## Result

- Added S027 visual QA cases for affine transform and `View2D` behavior.
- Added transform-query inverse fixture coverage through the Matplotlib reference query path.
- Updated status/spec closeout records and kept deferred public 3D/camera/controller semantics out
  of S027.
- Confirmed the P012 content from `ANSWER` is integrated in tracked ADR/spec/status records before
  removing the root file.
