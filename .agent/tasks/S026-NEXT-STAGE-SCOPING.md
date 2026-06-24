# S026 next stage scoping - Color Mapping and Colorbars

## Status

S026 is opened as the next protocol stage after completed S025 Mesh/3D Geometry.

## Selected direction: Color Mapping, Colorbars, and Scalar Data Semantics

Potential deliverables:

- shared colormap/normalization protocol contract;
- scalar-to-color mapping for a narrow accepted visual subset;
- query/readback semantics that distinguish source scalar values from displayed RGBA;
- colorbar or color-scale guide policy if accepted;
- Matplotlib reference rendering and query behavior;
- Datoviz v0.4 capability gates and structured unsupported diagnostics;
- VisPy2 producer API updates;
- visual QA cases for scalar/colorbar output.

## Consultation policy

Use ChatGPT Pro before committing public colormap, normalization, scalar-color, or colorbar
semantics. M090 created the self-contained P011 packet at
`.agent/consultations/P011-color-mapping-colorbars-scalar-semantics.md`. ADR/spec and
implementation missions remain blocked or draft until the response is accepted into durable
documents.

## Immediate next missions

| Mission | State | Purpose |
|---|---|---|
| M090 | completed | Opened S026 scoping and created P011 ChatGPT Pro consultation packet. |
| M091 | completed | Converted P011 response into ADR/spec baseline before implementation. |
| M092 | completed | Implemented accepted protocol dataclasses/enums/validation after M091. |
| M093 | completed | Added Matplotlib reference rendering/query behavior after M091/M092. |
| M094 | completed | Added visual QA cases and example coverage. |
| M095 | completed | Probed Datoviz v0.4 color mapping/colorbar capabilities. |
| M096 | completed | Added VisPy2 producer API updates after accepted semantics. |
