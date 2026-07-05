# M231 - S050 Datoviz post-refactor replay and result-code compatibility

## Stage

S050 - Post-S048 Implementation Roadmap And Datoviz Mesh-Pick Evidence

## Status

Completed by local-main-codex.

## Summary

Inspect the finished Datoviz `api/pre-rc-cleanup` branch, adapt GSP to Datoviz pre-RC mutator
`DvzResult` return codes, rerun the post-merge replay pack, and record comparison evidence.

## Required Context

- `.agent/S050_DATOVIZ_POST_MERGE_REPLAY_PREP.md`
- `.agent/S050_DATOVIZ_PRE_RC_COMPATIBILITY_REVIEW.md`
- `.agent/S050_DATOVIZ_TEXTURE2D_RUNTIME_SEMANTICS_PROOF.md`
- `tools/run_datoviz_pre_rc_replay.sh`
- `src/gsp_datoviz/protocol_renderer.py`
- `../datoviz/agents/now/STATUS.md`
- `../datoviz/agents/now/HANDOFF_PUBLIC_API_PRE_RC_AUDIT.md`

## Deliverables

- Inspect Datoviz branch state and active handoff notes.
- Patch GSP Datoviz adapter return-code handling for `DvzResult` mutators.
- Rerun Datoviz v0.4 smoke, guide-axis probe, S028 review pack, and baseline comparison.
- Commit replay evidence and Mission Control records.
- Keep M222 blocked unless Texture2D-specific blockers are resolved by fresh evidence.

## Acceptance

- Datoviz smoke passes against `/home/cyrille/GIT/Viz/datoviz`.
- S028 replay pack completes and comparison report is written.
- Focused tests and strict mypy pass.
- `tools/agentctl next` still reports M222 blocked.

## Stop Conditions

- Stop before editing the sibling Datoviz repository.
- Stop before advertising Datoviz Texture2D renderer capabilities.
- Stop before treating S028 crash reductions as Texture2D promotion evidence.

## Result

Completed locally. See `.agent/S050_DATOVIZ_POST_REFACTOR_REPLAY.md`.

The replay improved 10 Datoviz rows from crashed to strict with no regressions. Remaining crash rows
are colorbar and guide/View2D cases. M222 remains blocked.
