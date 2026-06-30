# M176 - S040 Datoviz Lambert strict promotion scoping

## Stage

S040 - Datoviz Strict Flat Lambert Promotion

## Status

Completed by local-main-codex.

## Summary

Open S040 as the backend-promotion stage after S039 and create a self-contained ChatGPT Pro
consultation packet before changing Datoviz Lambert behavior or capability advertisement.

## Deliverables

- S040 scoping note.
- P025 ChatGPT Pro consultation packet.
- Mission Control status update with dependent implementation/decision mission blocked pending P025.

## Acceptance

- S040 is explicitly bounded to Datoviz strict support for already accepted S039 flat Lambert
  semantics.
- The packet distinguishes CPU-resolved exact face colors from native Datoviz lighting.
- Datoviz implementation and capability promotion remain paused pending P025.

## Stop Condition

Stop if the next step tries to implement or advertise Datoviz `flat_lambert` support before P025 is
accepted into durable ADR/spec or decision authority.

## Result

Completed. Added `.agent/S040_SCOPING.md`, `.agent/consultations/P025-dataviz-s039-lambert-strict-promotion.md`,
and opened M177 as blocked pending P025.
