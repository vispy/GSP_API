# M073 - S024 Text/Glyph scoping and consultation

## Stage

S024 - Text/Glyph Visuals v1

## Status

Completed.

## Summary

Open S024 around Text/Glyph rather than Mesh, create a self-contained ChatGPT Pro consultation
packet, and gate dependent implementation until the response is available.

## Planned Deliverables

- Create `.agent/consultations/P009-text-glyph-protocol-semantics.md`.
- Update S024 scoping to select Text/Glyph as the next direction.
- Add Mission Control status records for S024, the open Pro question, and the blocked dependent
  follow-up mission.
- Do not implement public Text/Glyph semantics in this mission.

## Completed

- Created P009 with a self-contained prompt covering current accepted visual semantics, guide/text
  context, legacy text facts, Datoviz v0.4 constraints, exact design questions, and expected output.
- Updated `.agent/tasks/S024-NEXT-STAGE-SCOPING.md` to mark Text/Glyph selected and Pro-gated.
- Updated `.agent/status.json` with S024 in progress, M073 complete, M074 blocked pending P009, and
  open question Q070.

## Acceptance

A human can paste a single complete prompt into ChatGPT Pro. Dependent implementation is visibly
blocked until the consultation result is pasted or committed.

## Stop Condition

Stop if the work starts freezing TextVisual/GlyphVisual public fields or renderer behavior before the
P009 response is received and converted into ADR/spec updates.
