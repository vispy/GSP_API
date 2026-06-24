# M074 - S024 Text/Glyph ADR/spec baseline

## Stage

S024 - Text/Glyph Visuals v1

## Status

Blocked pending ChatGPT Pro consultation result.

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

## Acceptance

- Public Text/Glyph fields are documented before implementation.
- Font, size, anchor/alignment, rotation, Unicode/shaping, multiline, glyph atlas, query, and guide
  relationship decisions are explicitly recorded.
- Unsupported or deferred behavior has capability gates and diagnostics.

## Stop Condition

Stop until the P009 ChatGPT Pro result is available. Do not invent missing semantics from legacy
`Texts` code or backend APIs.
