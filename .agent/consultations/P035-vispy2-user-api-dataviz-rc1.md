# P035 - VisPy2 User API at the Datoviz v0.4 RC1 Boundary

## Exact prompt for ChatGPT Pro

You are reviewing the public user-side API boundary for an experimental scientific visualization
project. Produce a decisive architecture recommendation from the complete context below. Do not ask
for files or additional context. Do not assume that the package described here is the official
upstream VisPy 2.0 API.

### Project authority and architecture

The project charter defines:

- GSP as a backend-independent Graphics Server Protocol and session model for scientific
  visualization;
- VisPy2 as the high-level Python producer of GSP scenes;
- Matplotlib as the reference/conformance/publication backend;
- Datoviz v0.4 as the flagship local GPU backend;
- local desktop execution must have a fast in-process path with no mandatory JSON/base64;
- capability discovery and explicit adaptation are mandatory;
- unsupported behavior must be accepted, adapted with diagnostics, deactivated with diagnostics,
  or rejected explicitly;
- visual families are semantic contracts, not backend draw calls;
- query/readback and interaction are protocol features, not renderer-specific conveniences.

The mandated layering is:

```text
VisPy2 / plotting APIs / domain libraries
  -> GSP producer API
    -> GSP session and protocol model
      -> backend adapters
        -> Matplotlib reference backend
        -> Datoviz v0.4 GPU backend
```

An accepted documentation decision says the public mental model is a producer submitting semantic
commands and resources to a capability-negotiated GSP session, which executes through an adapter
and returns results and diagnostics. Direct protocol records are the lower-level integration and
conformance surface. Backend support must be stated per capability, not as a global interchangeable
backend claim.

### Current VisPy2 prototype

The Python package is currently named `vispy2`. It is an experimental GSP repository package, not
an official upstream VisPy release. Its API is deliberately small and Matplotlib-like:

```python
import vispy2 as vp

fig, ax = vp.subplots()
ax.set_xlim(-1, 1)
ax.set_ylim(-1, 1)
ax.set_xlabel("x")
ax.set_ylabel("y")
ax.set_title("Demo")
ax.grid(True)
ax.imshow(image, colormap="gray", clim=(0.0, 1.0))
ax.scatter(x, y, color=rgba, size=36)
ax.plot(x, y, color=rgba, width=4)
ax.mesh(positions, faces, color=rgba)
fig.render_matplotlib()
fig.savefig("out.png")
fig.show()
```

`Figure` retains axes and exposes semantic records through methods including `visuals()`,
`panels()`, `views()`, `attachments()`, `axis_guides()`, `panel_text_guides()`, `color_scales()`,
`texture_resources()`, and `colorbar_guides()`. Producer methods emit GSP records and must not call
Datoviz directly.

The current `Figure.render_matplotlib()` directly invokes the Matplotlib protocol-renderer helpers
and returns `(matplotlib_figure, matplotlib_axes)`. `savefig()` and `show()` are wrappers around that
path. There is no `render_datoviz()` or general user-facing GSP session execution method on
`Figure`. The lower-level Datoviz v0.4 adapter is mature enough for a bounded acceptance pack, but
capability coverage is uneven. Current evidence includes strict rendering for many points, markers,
paths, images, scalar-color, 2D mesh, and some retained 3D paths; some text and guide combinations
are adapted or crash; textured mesh promotion remains blocked; rich query parity is incomplete.

Datoviz v0.4 RC1 is imminent. The immediate proposed work is an acceptance pack that takes
representative VisPy2 scenes, lowers them to GSP, executes through Datoviz, records
strict/adapted/unsupported outcomes, generates paired Matplotlib/Datoviz artifacts, and freezes
payloads for post-RC replay. This acceptance work does not require a new public API.

### External positioning

The upstream VisPy website currently presents VisPy as a high-performance OpenGL-based interactive
2D/3D visualization library. Its roadmap discusses a future VisPy 2.0 direction, a better specified
plotting API, primitive visuals, reducing OpenGL leakage, possible Vulkan/WebGPU evolution, and
Datoviz as a possible future graphics backend. Therefore this project must avoid falsely implying
that its `vispy2` package is already the official upstream VisPy 2.0 API. At the same time, its GSP
and Datoviz work may provide useful evidence and design input for that future.

### Project owner decisions already recorded

The project owner has confirmed these product constraints:

1. Develop this VisPy2 work independently as evidence and later propose selected concepts upstream;
   do not present it as the official upstream VisPy 2 API.
2. Existing VisPy users do not necessarily need to recognize the API immediately, and drop-in
   compatibility is not a goal.
3. The central user promise is accepted: users write semantic scientific visualizations once and
   execute them through capability-aware backends, with Datoviz optimized for interactive GPU use
   and Matplotlib for reference/publication output.
4. GSP should remain invisible for simple plotting and become explicit for session selection,
   capability inspection, adaptations, diagnostics, and distributed use.

The owner also requires some intentionally experimental public VisPy2 API at this early stage. The
review must therefore distinguish a public producer API that can be documented and tested now from
an execution/session API whose stability may require post-RC evidence. “Make everything internal”
is not an acceptable recommendation.

### Decisions required

Recommend a minimal coherent user API for the next stage, addressing all of these questions:

1. Should backend/session selection live on `Figure`, in `vp.subplots(...)`, in a separate
   `Session`/`Runner`, or through another bounded pattern?
2. Should convenience calls be generic (`fig.show(session=...)`, `fig.render(...)`) or explicit
   (`render_matplotlib`, `show_datoviz`)? Explain how capability negotiation and diagnostics remain
   visible without making simple use cumbersome.
3. Define ownership and lifecycle for interactive Datoviz windows, blocking versus non-blocking
   execution, cleanup, retained updates, and return values.
4. Define how static publication output differs from interactive GPU display without pretending all
   backends offer the same operations.
5. Decide whether the current direct `render_matplotlib()` tuple return should remain, be deprecated,
   or be wrapped by a backend-neutral result type.
6. Recommend the smallest API needed for the RC acceptance stage versus what must wait until after
   RC1 evidence.
7. Identify user/product judgments that require the project owner's explicit decision, as distinct
   from engineering choices that can be delegated.
8. Recommend package naming and public wording that avoids collision or implied endorsement by
   upstream VisPy while preserving the project's stated VisPy2 goal.
9. Give representative code examples for: simple publication output, simple interactive Datoviz
   display, capability-aware execution with diagnostics, and retained interactive update.
10. List compatibility rules and stop conditions that prevent backend-specific concepts from
    leaking into the producer API.

Do not propose raw Datoviz handles on `Axes` or visual objects. Do not make JSON serialization
mandatory for local use. Do not claim backend parity. Prefer a small staged API over a complete
framework.

## Exact expected output format

Return one Markdown document with exactly these top-level sections:

1. `# Recommendation`
2. `## Decision Table` - columns: Decision, Recommendation, Rationale, Owner Approval Required
3. `## Minimal RC Stage` - explicit public API changes, internal-only acceptance work, and deferred work
4. `## Proposed API` - Python signatures and four runnable-style usage examples
5. `## Lifecycle Contract` - ownership, blocking, cleanup, updates, errors, diagnostics
6. `## Compatibility Contract` - compatibility guarantees and deprecation treatment
7. `## Naming and Positioning`
8. `## Owner Questions` - at most five crisp questions with a recommended default for each
9. `## Rejected Alternatives`
10. `## Stop Conditions`
11. `## ADR Draft` - concise decision record suitable for adaptation into the repository

Be decisive. Clearly label what can be implemented before Datoviz v0.4 RC1 and what requires
post-RC evidence. Keep the response under 3,500 words.
