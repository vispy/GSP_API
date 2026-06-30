# S039 Scoping - Lambert Normals Pre-Design

## Stage Goal

Decide whether GSP should accept a minimal Lambert-with-normals material model after S038, and if
so, define the smallest backend-neutral public semantics before any implementation begins.

## Context

S038 completed with a deliberately narrow boundary: existing `MeshVisual` RGBA colors are implicit
`unlit_rgba`, and public material objects, normals, lights, textures, UVs, and samplers remain
deferred.

The next smallest material expansion is Lambert-with-normals. It should not be implemented until the
protocol has accepted:

- normal source and cardinality;
- normal coordinate space and normalization policy;
- generated-normal policy, if any;
- material and light public fields;
- light direction space;
- diffuse color-combination rule;
- alpha and color-space boundary;
- strict/adapted backend expectations;
- conformance fixtures and diagnostics.

## Recommended Mission Stack

| Mission | State | Purpose |
|---|---|---|
| M170 | completed | Open S039 and create P024 ChatGPT Pro consultation packet. |
| M171 | blocked | Convert P024 response into ADR/spec baseline. |

## Stop Conditions

- Stop if Lambert requires accepting a broad material object/resource system.
- Stop if normal semantics cannot be specified without exposing backend-native shader/material state.
- Stop if the design tries to include textures/UVs in the same stage.
- Stop if implementation is requested before the P024 response is accepted into ADR/spec authority.

## Recommendation

Proceed with P024 consultation first. The expected outcome is either:

- a narrow S039 ADR/spec for Lambert-with-normals; or
- an explicit decision to defer Lambert and instead open a texture/UV or release-hardening stage.
