# M099-S027 - S027 P012 ADR/spec baseline

## Mission

M099

## Goal

Convert the P012 ChatGPT Pro response into accepted ADR/spec baselines for S027 transform, view,
camera deferral, navigation deferral, and query-inverse semantics.

## Status

Completed.

## Deliverables

- Add an ADR and relevant `spec/**` files for accepted S027 semantics.
- Update `SPEC_INDEX.md`, visual/capability/query/backend/VisPy2 docs, and decision records.
- Promote implementation missions only after the accepted baseline is recorded.

## Acceptance

- P012 response is available and captured.
- Public S027 semantics are documented before implementation.
- Mission Control status is updated before closeout.

## Stop Conditions

- Stop if P012 is unavailable.
- Stop if the response requires broader architecture decisions not contained in the packet.

## Completion Notes

- Preserved the ChatGPT Pro response as `.agent/consultations/P012-response.md`.
- Added ADR-0019 and `spec/transforms.md`.
- Added `.agent/decisions/S027_transform_view_contracts.md`.
- Updated `SPEC_INDEX.md`, protocol/query/capability/visual/backend/VisPy2 docs.
- Closed Q100 and promoted M100 to ready.
- Validation: `python3 -m json.tool .agent/status.json`; `tools/agentctl brief`;
  `tools/agentctl next`; `tools/agentctl review-now`; `git diff --check`.
