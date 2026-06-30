# M170 - S039 Lambert normals scoping and consultation

## Stage

S039 - Lambert Normals Pre-Design

## Status

Completed by local-main-codex.

## Summary

Open S039 as the next material-expansion decision after S038 and create a self-contained ChatGPT Pro
consultation packet before implementation or ADR/spec work begins.

## Deliverables

- S039 scoping note.
- P024 ChatGPT Pro consultation packet.
- Mission Control status update with dependent ADR/spec mission blocked pending P024.

## Acceptance

- S039 is explicitly bounded to Lambert-with-normals.
- Textures/UVs/samplers and Phong/specular remain out of scope.
- The consultation packet embeds all relevant accepted facts and expected output format.

## Stop Condition

Stop if the next step tries to implement Lambert or normals before P024 is accepted into durable
ADR/spec authority.

## Result

Completed. Added `.agent/S039_SCOPING.md`, `.agent/consultations/P024-lambert-normals-s039.md`, and
opened M171 as blocked pending P024.
