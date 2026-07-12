# S055 experimental Datoviz session preview closeout

Mission: M242

## Result

The independent `gsp_vispy2` producer now exposes a deliberately bounded experimental Datoviz
session surface:

- `open_session("datoviz")` with explicit context ownership;
- immutable capability inspection and structured diagnostics;
- pre-execution `inspect(...).require_executable()`;
- positive-frame-count blocking display;
- `block=False` display creation plus exactly one frame per `session.poll(display)`;
- opaque `Display` tokens without native backend handles;
- deterministic, idempotent cleanup;
- lifecycle errors for inspect, show, and poll after close.

Bare `Figure.show()` remains Matplotlib. Implicit temporary sessions, retained visual-data mutation,
generic `Display.update()`, close callbacks, and event-loop embedding guarantees remain deferred.

## Live evidence

The public example completed both modes against the installed Datoviz binding:

- bounded blocking execution: two frames, clean exit;
- explicit polling: two one-frame polls, clean exit.

## Validation

- full pytest: 657 passed, 2 skipped;
- focused session/lifecycle/producer pytest: 48 passed;
- strict mypy: clean across 219 source files;
- Ruff: clean;
- Matplotlib and Datoviz import smokes: clean;
- strict MkDocs build: clean;
- coverage run completed at 66% aggregate before the generated profile matrix was refreshed; the
  subsequent full suite was clean.

## Commits

- `17db4d6` agent: approve experimental Datoviz session preview
- `577c149` api: add bounded experimental Datoviz sessions
- `e1b2a2f` docs: publish experimental Datoviz session preview
- `9442f32` profiles: advertise bounded Datoviz session execution
