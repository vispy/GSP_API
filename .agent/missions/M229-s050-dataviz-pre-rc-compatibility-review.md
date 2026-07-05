# M229 - S050 Datoviz pre-RC compatibility review and handoff

## Stage

S050 - Post-S048 Implementation Roadmap And Datoviz Mesh-Pick Evidence

## Status

Completed by local-main-codex.

## Summary

Anticipate the sibling Datoviz `api/pre-rc-cleanup` branch in GSP, run a broad S028 compatibility
review pack, bound isolated Datoviz child runtime, and record an upstream Datoviz crash handoff plus
post-merge checklist.

## Required Context

- `../datoviz/agents/now/STATUS.md`
- `../datoviz/agents/now/HANDOFF_PUBLIC_API_PRE_RC_AUDIT.md`
- `../datoviz/spec/api/GSP_BACKEND_READINESS.md`
- `.agent/S050_DATOVIZ_OFFSCREEN_BATCH_CRASH_ISOLATION.md`
- `.agent/S050_DATOVIZ_TEXTURE2D_RUNTIME_SEMANTICS_PROOF.md`
- `spec/backends/datoviz.md`

## Deliverables

- Update the GSP Datoviz adapter for expected pre-RC symbol changes without Datoviz aliases.
- Add bounded runtime for isolated Datoviz offscreen child processes.
- Generate and commit an S028 compatibility review pack against the sibling Datoviz branch.
- Record a compact upstream Datoviz handoff and post-merge checklist.

## Acceptance

- `tools/datoviz_v04_smoke.py` passes against the sibling Datoviz checkout.
- Focused review-pack tests pass.
- New evidence is committed under `artifacts/visual_qa/s050/`.
- Mission Control records keep M222 blocked.

## Stop Conditions

- Stop before editing the sibling Datoviz repository.
- Stop before adding compatibility aliases for removed pre-RC Datoviz symbols.
- Stop before advertising Datoviz Texture2D renderer capabilities.
- Stop if Datoviz native crashes require debugger/source intervention; record an upstream handoff.

## Result

Completed locally. See `.agent/S050_DATOVIZ_PRE_RC_COMPATIBILITY_REVIEW.md`.

GSP commits:

- `c25d7da` Align GSP Datoviz adapter with pre-RC API
- `d1d3285` Bound isolated Datoviz review child runtime
- `178fd08` Record Datoviz pre-RC compatibility review pack

The broad review pack against Datoviz `api/pre-rc-cleanup` recorded 12 strict Datoviz rows, 4
adapted text rows, and 14 native SIGSEGV crash rows. M222 remains blocked.

