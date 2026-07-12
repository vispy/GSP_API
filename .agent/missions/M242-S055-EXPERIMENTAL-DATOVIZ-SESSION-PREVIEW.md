# M242 - S055 experimental Datoviz session preview

## Stage

S055 - Experimental Datoviz Session Preview

## Status

Approved.

## Summary

Implement the minimal explicit, bounded VisPy2 Datoviz session preview promoted by M235 lifecycle
evidence without changing the default Matplotlib producer behavior.

## Deliverables

- Publish `open_session("datoviz")` from `gsp_vispy2`.
- Expose immutable capability inspection and structured diagnostics.
- Support preflight inspection, bounded blocking display, and one-frame explicit-session polling.
- Make the session the sole owner of renderer and display lifecycle resources.
- Provide deterministic context-manager cleanup and idempotent close.
- Reject inspect, show, and poll operations after close with a public lifecycle error.
- Add focused tests, an experimental example, and public documentation.

## Acceptance

- `Figure.show()` remains the Matplotlib convenience path.
- Unsupported producer state rejects before Datoviz execution with structured diagnostics.
- Non-blocking/polled use requires an explicitly owned session.
- No native Datoviz handles are public.
- Focused lifecycle tests, strict mypy, backend import smokes, and the full suite pass.

## Path Locks

- `src/gsp_vispy2/**`
- `tests/test_vispy2_session.py`
- `examples/vispy2_datoviz_session.py`
- `spec/vispy2/**`
- `mkdocs_source/**session*`
- `.agent/S055_*`
- `.agent/missions/M242-*`
- `.agent/status.json`

## Stop Conditions

- Stop before implicit non-blocking temporary sessions or generic retained-data mutation.
- Stop before user/window-close callbacks or event-loop embedding guarantees.
- Stop before changing bare `Figure.show()` or storing backend state on producer objects.
- Stop before exposing native backend handles or editing the sibling Datoviz repository.
- Stop if implementation contradicts ADR-0033 or M235 lifecycle evidence.

## Approval

The project owner approved this bounded mission in the active Mission Control conversation and
instructed Mission Control to execute it with commits along the way.
