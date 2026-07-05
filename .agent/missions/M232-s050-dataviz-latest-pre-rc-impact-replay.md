# M232 - S050 Datoviz latest pre-RC compatibility impact replay

## Stage

S050 - Post-S048 Implementation Roadmap And Datoviz Mesh-Pick Evidence

## Status

Completed by local-main-codex.

## Summary

Refresh GSP's Datoviz compatibility evidence against the current sibling Datoviz
`api/pre-rc-cleanup` checkout after the post-M231 controller/result-contract and teardown changes.

## Required Context

- `.agent/S050_DATOVIZ_LATEST_PRE_RC_IMPACT_PLAN.md`
- `.agent/S050_DATOVIZ_POST_REFACTOR_REPLAY.md`
- `.agent/S050_DATOVIZ_PRE_RC_COMPATIBILITY_REVIEW.md`
- `.agent/S050_DATOVIZ_TEXTURE2D_RUNTIME_SEMANTICS_PROOF.md`
- `tools/run_datoviz_pre_rc_replay.sh`
- `src/gsp_datoviz/protocol_renderer.py`
- `src/gsp_datoviz/latest_api_contract.py`
- `../datoviz/agents/now/HANDOFF_PUBLIC_API_PRE_RC_AUDIT.md`
- `../datoviz/spec/scene/api/API_SURFACE.md`

## Deliverables

- Record the Datoviz branch, commit, and worktree cleanliness used for the replay.
- Audit post-M231 Datoviz API changes that overlap GSP adapter assumptions.
- Run the Datoviz v0.4 smoke and focused GSP Datoviz adapter tests.
- Replay the pre-RC Datoviz S028 review pack and compare it to M231 evidence.
- Update GSP adapter/spec/status only for fixture-backed compatibility changes.
- Keep M222 blocked unless Texture2D-specific sampler, origin, unmanaged RGBA, and exact unlit
  multiplication evidence is produced.

## Acceptance

- `tools/agentctl next` reports M232 as the suggested ready mission while M222 remains blocked.
- Current Datoviz commit and replay artifacts are recorded in an S050 evidence note.
- Focused Datoviz adapter validation passes or failures are documented with concrete blockers.
- Any capability promotion is backed by semantic fixture evidence, not just crash reduction.

## Stop Conditions

- Stop before editing the sibling Datoviz repository.
- Stop before advertising Datoviz Texture2D renderer capabilities.
- Stop before turning controller-native behavior into public GSP semantics without a protocol
  decision.
- Stop and create a ChatGPT Pro consultation packet if the Datoviz API changes require a GSP
  protocol redesign.

## Result

Completed locally. See `.agent/S050_DATOVIZ_LATEST_PRE_RC_REPLAY.md`.

GSP replayed Datoviz `api/pre-rc-cleanup` at `1ef626a56`. Fast adapter validation passed, the S028
compatibility matrix matched M231 exactly with zero regressions and zero improvements, and M222
remains blocked because Texture2D-specific sampler/origin/unmanaged-RGBA/unlit-equation evidence is
still absent.
