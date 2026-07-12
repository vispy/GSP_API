# M235 - S053 Datoviz live session lifecycle proof

## Stage

S053 - Datoviz Live Session Lifecycle Evidence

## Status

Approved.

## Summary

Establish bounded evidence for Datoviz live-window ownership, blocking and polled execution,
deterministic cleanup, and retained semantic updates before any public VisPy2 session-preview API is
implemented.

## Required Context

- `adr/ADR-0033-vispy2-producer-session-boundary.md`
- `.agent/S052_DATOVIZ_ACCEPTANCE_FAILURE_DECOMPOSITION.md`
- `.agent/S052_DATOVIZ_UPSTREAM_CTYPES_HANDOFF.md`
- `artifacts/visual_qa/s052/lifecycle/lifecycle_probe.json`
- `src/gsp_datoviz/protocol_renderer.py`
- `src/gsp/qa/live_review.py`
- `examples/protocol_live_window.py`
- `examples/protocol_live_interaction.py`
- `examples/protocol_live_view3d.py`

## Deliverables

- Inventory the current public Datoviz live-window, app-run, poll/frame, close, and callback APIs
  available through the generated binding; use public APIs only.
- Build internal subprocess probes for blocking display with automatic close, bounded polled display,
  explicit owner close, user/window close observation where automatable, and repeated open/close.
- Exercise at least one retained View2D update and one retained supported visual-data update without
  exposing raw Datoviz handles through VisPy2 objects.
- Record phase markers for create, attach, first frame, update, poll/run, close request, backend
  teardown, process exit, timeout, signal, and report completion.
- Test misuse boundaries: double close, update after close, poll after owner close, and hidden
  non-blocking ownership. Record which conditions can be enforced by a future session wrapper.
- Add focused tests and versioned evidence artifacts with Datoviz revision, platform, iteration
  counts, timing bounds, exit status, and diagnostics.
- Produce a promotion decision for a minimal experimental session preview; if evidence passes,
  draft but do not implement its exact bounded surface from ADR-0033.

## Acceptance

- Every probe runs in a bounded subprocess and cannot leave an unmanaged live window.
- Blocking and polled paths each have deterministic completion or an explicit failed result.
- Repeated lifecycle evidence includes at least five clean iterations for every passing path.
- Retained updates are verified from semantic GSP state or captured output, not only call counts.
- Cleanup failures, timeouts, and native signals remain backend failures.
- Focused pytest, strict mypy for changed modules, and backend imports pass.

## Path Locks

- `src/gsp/qa/**`
- `src/gsp_datoviz/**`
- `tests/test_*live*`
- `tests/test_navigation_smoke.py`
- `examples/protocol_live_*`
- `artifacts/visual_qa/s053/**`
- `.agent/S053_*`
- `spec/vispy2/**`

Existing unrelated documentation changes outside these paths must remain untouched.

## Stop Conditions

- Stop before adding or publishing `open_session()`, `Session`, `Display`, or `backend=` arguments.
- Stop before editing the sibling Datoviz repository, using private Datoviz APIs, or adding binding
  aliases/shims.
- Stop before exposing native handles, callbacks, or event-loop objects through VisPy2 producers.
- Stop if automated close is unavailable and a probe would require an unbounded/manual window.
- Stop and record a backend failure on timeout, signal, teardown abort, or ambiguous ownership.
- Stop and create a new architecture consultation if evidence contradicts ADR-0033 ownership or
  requires a new GSP lifecycle/event semantic.

## Approval

The project owner explicitly approved this next lifecycle-evidence mission in the active Mission
Control conversation and instructed Mission Control to execute it.
