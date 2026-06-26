# S027 next stage scoping - Transform, View, Camera, and Navigation

## Status

S027 is in progress after completed S026 Color Mapping, Colorbars, and Scalar Data Semantics.

## Selected direction

P012 accepted a 2D-first transform/view/query-inverse stage:

- finite invertible `AFFINE_2D` transform resources and inline visual transform bindings;
- deterministic linear panel `View2D` with explicit `xlim`/`ylim`;
- required transformed query inverse/readout payloads for strict support;
- capability gates for backend transform placement and unsupported projections;
- Matplotlib strict reference behavior;
- Datoviz native/adapted/unsupported reporting without hidden virtual-source materialization;
- VisPy2 producer API updates that emit protocol records;
- public 3D camera, projection, controller/navigation events, transform graphs, nonlinear
  transforms, and layout/aspect semantics deferred.

## Consultation policy

P012 is answered and captured at `.agent/consultations/P012-response.md`. M099 converted it into
ADR-0019, `spec/transforms.md`, and S027 decision records. Further ChatGPT Pro consultation is not
required unless a later mission needs to expand public 3D camera/projection/controller or transform
graph semantics.

## Immediate next missions

| Mission | State | Purpose |
|---|---|---|
| M098 | completed | Opened S027 scoping and created P012 ChatGPT Pro consultation packet. |
| M099 | completed | Converted P012 response into ADR/spec baseline before implementation. |
| M100 | ready | Implement accepted protocol dataclasses/enums/validation. |
| M101 | blocked | Add Matplotlib reference transform/query behavior after M100. |
| M102 | blocked | Add Datoviz transform capability gates or bounded runtime mapping. |
| M103 | blocked | Add VisPy2 producer API updates after protocol models exist. |
| M104 | blocked | Add QA fixtures and close S027. |
