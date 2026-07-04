# M217 - S050 Datoviz offscreen batch crash isolation

## Stage

S050 - Post-S048 Implementation Roadmap And Datoviz Mesh-Pick Evidence

## Status

Completed by local-main-codex.

## Summary

Isolate the remaining Datoviz offscreen child-process crash seen in combined multi-case review packs,
starting with the M208 five-case TextVisual batch. Determine whether the failure is a GSP lifecycle
bug, a Datoviz offscreen/runtime teardown bug, or a known upstream limitation that should stay
isolated by one-case child processes.

## Required Context

- `.agent/S050_DATOVIZ_TEXTVISUAL_STRICTNESS_PROOF.md`
- `.agent/S050_DATOVIZ_LIVE_POINT_IMAGE_PAYLOAD_EVIDENCE.md`
- `artifacts/visual_qa/s050/m208-textvisual-strictness/`
- `artifacts/visual_qa/s050/m208-textvisual-strictness-isolated/`
- `tools/run_datoviz_visual_review_pack.sh`
- `src/gsp/qa/visual/review_pack.py`
- `src/gsp/qa/visual/runner.py`
- `src/gsp_datoviz/protocol_renderer.py`

## Acceptance

- Reproduce the combined TextVisual crash with the current Datoviz checkout.
- Narrow the crash to a minimal sequence or classify it as upstream/native lifecycle behavior.
- If the fix is in GSP, implement it without changing public visual/query semantics.
- If the fix belongs in Datoviz, record a focused handoff and keep GSP review packs isolated.
- Preserve the latest-only Datoviz v0.4-dev generated binding contract.

## Stop Conditions

- Stop before editing the sibling Datoviz repository.
- Stop before adding compatibility shims or legacy query/visual aliases.
- Stop if native crash diagnosis requires Datoviz source changes or debugger-only intervention; record a handoff instead.

## Result

Completed locally. See `.agent/S050_DATOVIZ_OFFSCREEN_BATCH_CRASH_ISOLATION.md`.

Outcome: the current Datoviz v0.4-dev checkout still reproduces the combined TextVisual batch crash
as child signal 11. Direct child probes narrowed the behavior to Datoviz/native lifecycle teardown:
single-case text runs write complete PNG and `report.json` artifacts before some processes segfault
during garbage collection with no Python frame.

The GSP review-pack isolation layer now runs Datoviz offscreen review packs one child process per
case. If a child writes a complete report and then crashes during native teardown, the parent keeps
the rendered artifact and writes a `*.child_teardown_crash.json` evidence file. Missing reports still
remain structured crash rows.

No sibling Datoviz files were edited. No public visual or query semantics changed.
