# M243 - S056 public session conformance and failure-isolation hardening

## Stage

S056 - Public Session Conformance And Failure Isolation

## Status

Completed.

## Summary

Harden the bounded experimental Datoviz session preview with representative public-producer
conformance, normalized failures, deterministic partial-construction cleanup, and isolated repeated
live evidence without expanding the API.

## Deliverables

- Normalize renderer creation, attachment, blocking, and polling failures as structured public
  session execution errors.
- Guarantee cleanup when renderer construction or scene attachment fails partway through.
- Verify multiple display ownership, context exceptions, double close, foreign displays, and all
  post-close operations.
- Exercise representative supported and unsupported producer scenes before app execution.
- Add bounded subprocess evidence for repeated public blocking and polling lifecycles.
- Record machine-readable public-session evidence and a promotion/remaining-gates decision.

## Acceptance

- Five clean repetitions for every promoted public lifecycle mode.
- Unsupported producer combinations do not enter `dvz_app_run`.
- Native timeouts, signals, and adapter failures remain backend failures with structured diagnostics.
- No raw Datoviz exception escapes `Session.show()` or `Session.poll()`.
- Focused tests, strict mypy, Ruff, backend imports, strict docs, and the full suite pass.

## Path Locks

- `src/gsp_vispy2/session.py`
- `src/gsp/qa/public_session_probe.py`
- `tests/test_vispy2_session.py`
- `tests/test_public_session_probe.py`
- `artifacts/visual_qa/s056/**`
- `spec/vispy2/session_preview_s053.md`
- `.agent/S056_*`
- `.agent/missions/M243-*`
- `.agent/status.json`

## Stop Conditions

- Stop before adding retained `Display.update()`, close callbacks, implicit sessions, or embedding
  guarantees.
- Stop before changing bare `Figure.show()` or exposing native handles.
- Stop before editing external repositories or treating a native signal/timeout as success.
- Stop and report if public-wrapper evidence contradicts ADR-0033 or M235 ownership evidence.

## Approval

The project owner explicitly approved this mission and authorized pushing its traceable commits to
`origin/main` in the active Mission Control conversation.

## Result

Completed and pushed. Public session failures are normalized, partial and exceptional lifecycle
paths clean up deterministically, representative producer routing is covered, and ten isolated live
public lifecycles passed with zero timeouts. Full validation passed with 666 tests and 2 skips, 66%
aggregate coverage, strict mypy clean across 220 source files, Ruff clean, both backend imports
clean, strict documentation clean, and profile consistency clean.
