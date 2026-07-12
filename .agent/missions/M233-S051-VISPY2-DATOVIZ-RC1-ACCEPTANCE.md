# M233 - S051 VisPy2 to Datoviz RC1 acceptance pack

## Stage

S051 - VisPy2 Public Producer And Datoviz RC1 Acceptance

## Status

Approved.

## Summary

Validate representative scenes authored through the public experimental VisPy2 producer API by
lowering them to in-memory GSP records and executing them through the Matplotlib reference and
Datoviz v0.4 pre-RC adapters. Preserve evidence needed to decide whether a post-RC public session
preview is viable.

## Required Context

- `adr/ADR-0033-vispy2-producer-session-boundary.md`
- `.agent/consultations/P035-response.md`
- `spec/vispy2/api.md`
- `spec/vispy2_visual_api.md`
- `src/vispy2/protocol.py`
- `src/gsp/qa/visual/`
- `src/gsp_datoviz/protocol_renderer.py`
- `.agent/S050_DATOVIZ_LATEST_PRE_RC_REPLAY.md`

## Deliverables

- Define a representative, bounded VisPy2 acceptance scene matrix covering supported public
  producer families and known capability boundaries.
- Add an internal adapter from a VisPy2 `Figure` to the existing in-memory visual-QA scene model,
  without JSON/base64 in the local execution path.
- Execute paired Matplotlib and Datoviz acceptance artifacts using existing crash isolation.
- Classify each backend outcome as strict, adapted, deactivated, unsupported, or backend failure,
  with structured diagnostics and semantic record IDs where available.
- Write a machine-readable manifest containing producer/API version, GSP schema version, backend and
  Datoviz commit/version evidence, capability snapshot, platform, artifact paths, and hashes.
- Freeze versioned replay fixtures sufficient for post-RC1 comparison.
- Add focused tests and a durable S051 evidence note describing whether the post-RC preview session
  promotion conditions are met.

## Acceptance

- Every selected scene is authored through public `vispy2` calls, not private QA scene builders.
- Matplotlib and Datoviz consume equivalent semantic GSP scene records for each paired case.
- Silent drops are treated as failures; adaptations and deactivations carry diagnostics.
- Crash-prone Datoviz cases remain isolated and preserve any complete pre-crash report or artifact.
- Focused producer, QA, manifest, and replay tests pass.
- No public session API or renderer capability is promoted solely from this pack.

## Path Locks

- `src/vispy2/**`
- `src/gsp/qa/visual/**`
- `tests/test_vispy2*`
- `tests/test_visual_qa_harness.py`
- `examples/vispy2_*`
- `artifacts/visual_qa/s051/**`
- `.agent/S051_*`
- `spec/vispy2*`

Existing unrelated documentation changes outside these paths must remain untouched.

## Stop Conditions

- Stop before adding `open_session()`, `backend=` convenience arguments, a public `Display`, or a
  public Datoviz execution method.
- Stop before changing the existing `render_matplotlib()` tuple contract.
- Stop before advertising a Datoviz capability without independent semantic fixture evidence.
- Stop before editing the sibling Datoviz repository, using private Datoviz APIs, or adding
  compatibility aliases for removed pre-RC symbols.
- Stop and report if equivalent public VisPy2 scenes cannot be represented by the accepted GSP scene
  model without a protocol or public API redesign.
- Stop and create a new ChatGPT Pro consultation if evidence requires changing ADR-0033 lifecycle or
  producer/session ownership decisions.

## Approval

The project owner approved the proposed VisPy2 to GSP to Datoviz RC1 acceptance pack in the active
Mission Control conversation and instructed Mission Control to continue with commits along the way.
