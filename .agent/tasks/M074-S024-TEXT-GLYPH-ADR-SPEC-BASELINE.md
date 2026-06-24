# M074-S024-TEXT-GLYPH-ADR-SPEC-BASELINE - Text/Glyph ADR/spec baseline

## Mission

M074

## Goal

After P009 is answered, convert the consultation result into durable Text/Glyph protocol decisions
and mission-sized implementation tasks.

## Blocker

Awaiting ChatGPT Pro response for `.agent/consultations/P009-text-glyph-protocol-semantics.md`.

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
