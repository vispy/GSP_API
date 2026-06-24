# M074-S024-TEXT-GLYPH-ADR-SPEC-BASELINE - Text/Glyph ADR/spec baseline

## Mission

M074

## Goal

After P009 is answered, convert the consultation result into durable Text/Glyph protocol decisions
and mission-sized implementation tasks.

## Status

Completed. P009 response saved and converted into ADR/spec/task records.

## Required Work After Response

- Save the response as `.agent/consultations/P009-response.md`.
- Draft/accept an ADR for Text/Glyph v1 semantics.
- Create/update the relevant `spec/visuals/*` files.
- Update capability, Datoviz, visual QA, VisPy2 API, and spec index docs.
- Create implementation missions with stop conditions.

## Acceptance

- Text/Glyph implementation can begin without workers inventing protocol fields.
- Remaining uncertainty is represented as explicit deferred scope or capability-gated diagnostics.

## Stop Conditions

- Stop if no P009 response exists.
- Stop if P009 leaves a key design decision unresolved and no safe narrow default is stated.

## Completion Notes

- Added `.agent/consultations/P009-response.md`.
- Added ADR-0016, `spec/visuals/text.md`, and `.agent/decisions/S024_textvisual_contracts.md`.
- Updated relevant spec indexes and capability/query/QA/backend notes.
- Created M075-M081 follow-up missions; M075 is ready.
