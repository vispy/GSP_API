# ADR-0033: VisPy2 Producer And Session Boundary

Status: accepted

## Context

VisPy2 is the experimental high-level Python producer for GSP. Its current public surface constructs
backend-independent figures, axes, visuals, guides, and resources, while its convenience execution
path calls the Matplotlib reference renderer directly. Datoviz v0.4 RC1 is approaching, but strict
support remains capability-specific and some guide, text, texture, and query paths are adapted,
unsupported, or unstable.

The project needs a useful public producer API now without freezing an unproven interactive
execution lifecycle or implying that this independent prototype is the official upstream VisPy 2
API.

## Decision

The existing `Figure`, `Axes`, plotting methods, semantic record accessors, and Matplotlib
publication conveniences remain an experimental public producer API through the Datoviz v0.4 RC1
acceptance stage. Figures own semantic producer state only. Backend, device, adapter, window, event
loop, and execution-resource state must not be stored on figures, axes, or visuals.

Before RC1, Datoviz execution remains an internal acceptance path. It will lower representative
public VisPy2 scenes to in-memory GSP records, execute them through the Matplotlib and Datoviz
adapters, classify outcomes, preserve diagnostics and artifacts, and freeze versioned replay
fixtures. This work must not require JSON or base64 for local execution.

After RC1 evidence satisfies the stop conditions below, backend selection will be introduced through
a capability-negotiated `Session`, created by `open_session()`. Operation-specific `show()` and
`savefig()` conveniences may accept either an explicit session or a one-shot backend name. Backend
selection must not be added to `subplots()`, retained on `Figure`, or exposed through backend-named
methods such as `show_datoviz()`.

An explicit session owns capabilities, adapter state, backend resources, event-loop integration,
and displays. Non-blocking display requires an explicit session. Adapted and deactivated behavior
warns by default; unsupported behavior rejects before execution. Matplotlib remains the default for
bare `show()` and `savefig()` during 0.x.

`render_matplotlib()` retains its tuple contract through RC1. A later session-backed
`MatplotlibRenderResult` may replace it with one documented deprecation cycle while preserving
explicit native Matplotlib interoperability.

The intended external identity is `gsp-vispy2` for the distribution and `gsp_vispy2` for the import.
The existing `vispy2` import may remain temporarily as a compatibility alias. Public wording must
state that this is an independent experimental GSP producer, not an official upstream VisPy 2.0
release. Drop-in compatibility with current VisPy or Matplotlib is not a goal.

## Consequences

- The RC acceptance pack validates the real public producer surface rather than a private scene
  builder.
- Simple plotting remains concise while capability inspection and lifecycle ownership have a clear
  future home.
- No public Datoviz execution contract is promised from pre-RC adapter evidence.
- Backend-specific handles, pipelines, shaders, and event objects remain outside producer methods.
- Producer compatibility means preserving semantic intent, not pixel identity or universal backend
  parity.

## Promotion Conditions

Do not publish the session API until representative scenes classify without silent drops, known
crashes are fixed or rejected before execution, all adaptations and deactivations produce structured
diagnostics, blocking cleanup is deterministic, non-blocking ownership is unambiguous, and repeated
create/show/close cycles do not leak backend resources.

## Basis

Accepted from the P035 ChatGPT Pro consultation in
`.agent/consultations/P035-response.md`, with the project owner's recorded product constraints in
`.agent/consultations/P035-vispy2-user-api-dataviz-rc1.md`.
