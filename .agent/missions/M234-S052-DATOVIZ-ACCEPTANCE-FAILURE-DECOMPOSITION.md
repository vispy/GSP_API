# M234 - S052 Datoviz acceptance failure decomposition and preflight hardening

## Stage

S052 - Datoviz RC1 Acceptance Failure Decomposition

## Status

Approved.

## Summary

Decompose the three native Datoviz failures recorded by the S051 public VisPy2 acceptance pack,
identify their execution phase and minimal semantic trigger, and harden internal capability preflight
only where an unsupported combination can be identified before native execution.

## Required Context

- `.agent/S051_VISPY2_DATOVIZ_RC1_ACCEPTANCE.md`
- `artifacts/visual_qa/s051/rc1-acceptance/acceptance_manifest.json`
- `adr/ADR-0033-vispy2-producer-session-boundary.md`
- `spec/vispy2/acceptance_s051.md`
- `src/gsp/qa/visual/vispy2_acceptance.py`
- `src/gsp/qa/visual/review_pack.py`
- `src/gsp/qa/visual/runner.py`
- `src/gsp_datoviz/protocol_renderer.py`

## Deliverables

- Reduce `vispy2/primitives`, `vispy2/text`, and `vispy2/mesh` into individual visual, guide, and
  resource combinations until each native abort has a minimal trigger or is shown to be teardown-
  only after a complete render report.
- Record whether each failure occurs during capability inspection, scene creation, upload,
  rendering, capture, report writing, or teardown.
- Compare minimized VisPy2 scenes with semantically equivalent S028/S029/S051 QA cases and explain
  any difference in records, resources, coordinate spaces, guides, or execution configuration.
- Add internal preflight rejection only for semantic combinations already proven unsupported and
  detectable before execution; preserve native defects as backend failures.
- Run repeated create/capture/close probes for the surviving supported intersection and record
  deterministic lifecycle evidence or the precise remaining instability.
- Add focused regression tests, refreshed acceptance evidence, and a self-contained upstream
  Datoviz handoff for every native issue requiring upstream work.

## Acceptance

- Every original S051 Datoviz failure has a classified execution phase and a minimal reproducer or
  a documented lower bound on the trigger.
- No native abort is silently reclassified as unsupported.
- Preflight diagnostics name semantic capabilities and record IDs rather than Datoviz handles.
- Existing S028/S029 strict rows do not regress.
- Supported lifecycle probes run in isolated processes and report iteration count, phase, exit
  status, artifact/report completeness, and Datoviz revision.
- Focused tests and strict mypy for changed modules pass.

## Path Locks

- `src/gsp/qa/visual/**`
- `src/gsp_datoviz/**`
- `tests/test_vispy2_s051_acceptance.py`
- `tests/test_visual_qa_harness.py`
- `artifacts/visual_qa/s052/**`
- `.agent/S052_*`
- `spec/vispy2/acceptance_s051.md`

Existing unrelated documentation changes outside these paths must remain untouched.

## Stop Conditions

- Stop before adding or publishing `open_session()`, `Session`, `Display`, `backend=`, or a public
  Datoviz execution convenience.
- Stop before editing the sibling Datoviz repository or using private Datoviz APIs.
- Stop before advertising a new renderer capability without independent semantic fixture evidence.
- Stop before treating signal 6, signal 11, timeout, teardown abort, or missing report as ordinary
  unsupported behavior.
- Stop and create a separate architecture consultation if the diagnosis requires changing GSP
  semantics or the ADR-0033 producer/session ownership boundary.

## Approval

The project owner explicitly approved this recommended mission in the active Mission Control
conversation and instructed Mission Control to execute it.
