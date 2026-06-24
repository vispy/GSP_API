# M091-S026 - S026 P011 ADR/spec baseline

## Mission

M091

## Goal

Convert the P011 ChatGPT Pro response into accepted ADR/spec baselines for color mapping,
colorbars, normalization, scalar visual integration, and query/readback semantics.

## Status

Completed.

## Deliverables

- Add an ADR and relevant `spec/**` files for accepted S026 semantics.
- Update `SPEC_INDEX.md`, visual/capability/query/backend/VisPy2 docs, and decision records.
- Promote implementation missions only after the accepted baseline is recorded.

## Acceptance

- P011 response is available and captured.
- Public S026 semantics are documented before implementation.
- Mission Control status is updated before closeout.

## Stop Conditions

- Stop if P011 is unavailable.
- Stop if the response requires broader architecture decisions not contained in the packet.

## Completion Notes

- Preserved the ChatGPT Pro response as `.agent/consultations/P011-response.md`.
- Added ADR-0018 and `spec/color_mapping.md`.
- Added `.agent/decisions/S026_color_mapping_contracts.md`.
- Updated `SPEC_INDEX.md`, image/query/visual-family/cross-cutting/capability/QA/VisPy2/Datoviz
  docs.
- Closed Q090 and promoted M092 to ready.
- Validation: `python3 -m json.tool .agent/status.json`; `tools/agentctl brief`;
  `tools/agentctl next`; `git diff --check`.
