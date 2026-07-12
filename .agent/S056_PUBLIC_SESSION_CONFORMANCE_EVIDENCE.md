# S056 public session conformance evidence

Mission: M243

## Public boundary hardening

`Session.show()` now normalizes renderer creation and partial scene-attachment failures into
`SessionExecutionError` with `session.backend.preparation_failed`. Blocking and polling failures use
`session.backend.execution_failed` and `session.backend.poll_failed`. Partially prepared renderers,
blocking failures, context exceptions, multiple owned displays, and repeated close all clean up
deterministically.

Focused producer coverage routes point, image, text, mesh, native axes, and colorbar records before
execution. Multi-axes and panel-text-guide combinations remain preflight rejections and do not
construct a renderer or enter `dvz_app_run`.

## Isolated live evidence

Artifact: `artifacts/visual_qa/s056/public-session/public_session_probe.json`

| Mode | Iterations | Clean exits | Timeouts |
|---|---:|---:|---:|
| Bounded two-frame blocking | 5 | 5 | 0 |
| Explicit two-call one-frame polling | 5 | 5 | 0 |

Every subprocess reported inspection completion, execution completion, session closure, exit code
zero, and no public diagnostic error.

## Decision

The bounded experimental preview is conformance-ready at its existing scope. This evidence does not
promote retained `Display.update()`, implicit sessions, user/window-close callbacks, thread-affinity
semantics, or event-loop embedding guarantees.

## Validation

- full pytest with coverage: 666 passed, 2 skipped; 66% aggregate coverage;
- focused public session and probe tests: 16 passed;
- strict mypy: clean across 220 source files;
- Ruff: clean across source, tests, and examples;
- Matplotlib and Datoviz backend import smokes: clean;
- strict MkDocs and profile consistency: clean.
