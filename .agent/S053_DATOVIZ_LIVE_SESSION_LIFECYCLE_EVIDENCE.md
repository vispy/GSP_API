# S053 Datoviz live session lifecycle evidence

Date: 2026-07-12

Mission: M235

## API inventory

The current generated Datoviz v0.4 binding exposes `dvz_app_run(app, frame_count)` and public input
and frame callback APIs. It does not expose a separate application poll function or a bounded
window-close request suitable for this proof. GSP's internal renderer maps `show(frame_count=N)` to
`dvz_app_run`; repeated `frame_count=1` calls provide bounded explicit polling. Renderer ownership is
closed through `dvz_app_destroy` and `dvz_scene_destroy`, with idempotent `close()`.

## Evidence

`artifacts/visual_qa/s053/live-session/live_session_probe.json` records five isolated iterations for
each mode:

| Mode | Iterations | Clean exit | Complete report | Timeout |
|---|---:|---:|---:|---:|
| bounded two-frame run | 5 | 5 | 5 | 0 |
| three explicit one-frame polls | 5 | 5 | 5 | 0 |
| retained View2D update | 5 | 5 | 5 | 0 |

Every retained View2D iteration captured deterministic but different before/after PNG hashes,
proving output changed from semantic View2D state rather than only recording native call counts.
Every child recorded create, visual attachment, first-frame/update, close request, owner close, and
idempotent double-close phases.

## Misuse boundary

The internal renderer makes double close idempotent but does not currently reject show, poll, or
retained update after close. A public session wrapper must enforce these states before delegating:

- show/update/poll after owner close raises `LifecycleError`;
- hidden non-blocking temporary ownership is forbidden;
- non-blocking/polled execution requires an explicit session context;
- backend signals, timeout, or teardown abort remain `BackendExecutionError`.

Automated user/window-close observation was not proven because no bounded public close-request API
was available. The proof used frame-count completion and explicit owner close only.

## Promotion decision

A minimal **experimental** session preview may now be implemented for explicit Datoviz selection,
bounded blocking display, explicit-session one-frame polling, deterministic context cleanup,
capability inspection, and structured diagnostics. Bare `Figure.show()` remains Matplotlib during
0.x, and `subplots()` remains backend-independent.

Retained visual-data replacement, user-driven close observation, implicit non-blocking sessions,
callback/event-loop interop, and a stable `Display.update()` contract remain deferred. Retained
View2D evidence may support internal navigation but does not by itself promote general retained
updates.
