# M074 - S024 Text/Glyph ADR/spec baseline

## Stage

S024 - Text/Glyph Visuals v1

## Status

Completed.

## Summary

Convert the P009 ChatGPT Pro response into accepted ADR/spec/task updates for the Text/Glyph visual
family before implementation begins.

## Planned Deliverables

- `.agent/consultations/P009-response.md` or equivalent committed/pasted response intake.
- Accepted ADR for Text/Glyph v1 protocol semantics.
- `spec/visuals/text.md` and/or `spec/visuals/glyph.md` as recommended by P009.
- Updates to visual cross-cutting rules, capability schema, Datoviz boundary, visual QA spec, and
  VisPy2 API spec as needed.
- Follow-up implementation missions for Matplotlib reference rendering, Datoviz capability-gated
  support, VisPy2 producer APIs, tests, and visual QA cases.

## Completed

- Saved the ChatGPT Pro answer as `.agent/consultations/P009-response.md`.
- Accepted ADR-0016 and `spec/visuals/text.md` for `TextVisual` v1.
- Updated spec indexes, visual-family docs, capability/query notes, Datoviz boundary, visual QA plan, and VisPy2 visual API notes.
- Added `.agent/decisions/S024_textvisual_contracts.md`.
- Created follow-up missions M075-M081.

## Acceptance

- Public Text/Glyph fields are documented before implementation.
- Font, size, anchor/alignment, rotation, Unicode/shaping, multiline, glyph atlas, query, and guide
  relationship decisions are explicitly recorded.
- Unsupported or deferred behavior has capability gates and diagnostics.

## Stop Condition

Stop if implementation starts before M075 or if workers add public glyph/atlas/font-handle fields outside ADR-0016.
