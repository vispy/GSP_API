# M199 - S050 implementation roadmap and mission batch

## Stage

S050 - Post-S048 Implementation Roadmap And Datoviz Mesh-Pick Evidence

## Status

Completed by local-main-codex.

## Summary

Reconcile the Mission Control status after the S049 white paper draft, then open the next
implementation branch requested by the user. The branch should prioritize Datoviz native
mesh-picking evidence, followed by query/readback parity, strict guide/text/colorbar review rows,
strict 3D raster semantics, and later API-shape consultations.

## Deliverables

- Register existing S049/M198 white paper records in `.agent/status.json`.
- Add `.agent/S050_SCOPING.md`.
- Add mission records M199-M204.
- Mark M200 approved as the next executable mission.
- Preserve release and capability-promotion stop conditions.

## Acceptance

- `tools/agentctl next` reports M200 as the approved next mission.
- M200 has explicit stop conditions around Datoviz capability promotion and sibling-repo edits.
- Materials/textures and broader VisPy2 API work remain blocked pending ChatGPT Pro consultation.

## Result

Completed locally. See `.agent/S050_SCOPING.md`.
