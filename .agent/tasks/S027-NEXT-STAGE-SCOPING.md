# S027 next stage scoping - Transform, View, Camera, and Navigation

## Status

S027 is opened as the next GSP protocol stage after completed S026 Color Mapping, Colorbars, and
Scalar Data Semantics.

## Selected direction

Transform, view, camera, navigation, and query-inverse semantics.

Potential deliverables after ChatGPT Pro response:

- shared transform/view protocol contract;
- deterministic 2D data/view transform baseline;
- minimal or deferred 3D camera policy;
- query/readback inverse-transform semantics;
- capability gates for backend transform placement and unsupported projections;
- Matplotlib reference behavior;
- Datoviz capability mapping and structured unsupported diagnostics;
- VisPy2 producer API updates;
- visual QA cases for transformed scenes and queries.

## Consultation policy

Use ChatGPT Pro before committing public transform, view, camera, controller/navigation, layout, or
query-inverse semantics. M098 created the self-contained P012 packet at
`.agent/consultations/P012-transform-view-camera-navigation-semantics.md`. ADR/spec and
implementation missions remain blocked or draft until the response is accepted into durable
documents.

## Immediate next missions

| Mission | State | Purpose |
|---|---|---|
| M098 | completed | Opened S027 scoping and created P012 ChatGPT Pro consultation packet. |
| M099 | blocked | Convert P012 response into ADR/spec baseline before implementation. |
| M100 | blocked | Implement accepted protocol dataclasses/enums/validation after M099. |
| M101 | blocked | Add Matplotlib reference transform/query behavior after M099/M100. |
| M102 | blocked | Add Datoviz transform capability gates or bounded runtime mapping. |
| M103 | blocked | Add VisPy2 producer API updates after accepted semantics. |
| M104 | blocked | Add QA fixtures and close S027. |
