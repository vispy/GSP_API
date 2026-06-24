# M096 - S026 VisPy2 color mapping producer API

## Stage

S026 - Color Mapping, Colorbars, and Scalar Data Semantics

## Status

Completed.

## Summary

Expose accepted S026 color mapping/colorbar/scalar behavior through VisPy2 producer APIs.

## Planned Deliverables

- Completed: Producer APIs.
- Completed: Examples and focused tests.

## Outcome

VisPy2 now exposes bounded S026 producer APIs for semantic `ColorScale`
resources, scalar image color-scale linkage, point color scalar encodings,
marker fill scalar encodings, and `ColorbarGuide` intent. The API emits formal
GSP protocol objects and keeps Datoviz shader/slot details and Matplotlib
mappable objects out of the public surface. Scalar color creation requires
explicit `clim` or an existing `ColorScale`, preserving the accepted no-auto
normalization constraint.

## Acceptance

- M091 baseline exists.
- API emits formal GSP protocol scenes and avoids backend-specific controls.

## Stop Condition

Stop if the API would expose unaccepted color mapping semantics.
