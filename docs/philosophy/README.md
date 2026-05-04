# GSP_API — Philosophy & Design Documents

This folder collects the prose documentation behind GSP_API: one academic-style white paper and four "philosophy" essays that explain why the codebase is shaped the way it is. Each document exists in three forms — a Markdown source (`*.md`), a rendered PDF (`*.pdf`), and the prompt used to generate it (`*_prompt.md`) where applicable. The PDFs below are the reading-friendly version; open the `.md` next to each one to see the source or follow inline links into the code.

## Documents

### [whitepaper.pdf](./whitepaper.pdf)
A self-contained white paper presenting GSP_API as a backend-agnostic scene-description API for 2D/3D scientific visualization in Python. It motivates the split between scene description and rendering, frames GSP_API against Matplotlib, Datoviz, VisPy, Plotly, and Bokeh, and describes the architecture, trade-offs, security posture, and current research-prototype status (v0.1.0). Read this first if you want the high-level pitch and how the project positions itself in the ecosystem.

### [philosophy_packages.pdf](./philosophy_packages.pdf)
A tour of the seven Python packages under [src/](../../src/) and the three-tier layered architecture (contract → backend → convenience) that governs how they depend on each other. It enforces the "dependencies point downward" rule with grep recipes you can run to verify any claim, and walks each package's role: `gsp`, `gsp_matplotlib`, `gsp_datoviz`, `gsp_network`, `gsp_extra`, `gsp_pydantic`, `vispy2`. Read this second to get the map of the repo before drilling into any one package.

### [philosophy_gsp_core.pdf](./philosophy_gsp_core.pdf)
A deep dive on [`src/gsp/`](../../src/gsp/), the contract layer that every backend implements and every convenience layer builds on. It covers the five design principles (contract not implementation, data not commands, lazy data via `TransBuf`, self-registration over manifests, numpy + stdlib only) and explains how `Canvas`, `Viewport`, `Camera`, `Buffer`, and `Visual` are defined without committing to how rendering happens. Read this when you are about to modify or extend the abstract protocol.

### [philosophy_renderers.pdf](./philosophy_renderers.pdf)
A reading guide to the three renderer packages — `gsp_matplotlib`, `gsp_datoviz`, `gsp_network` — and the conventions that make them a coherent ecosystem rather than three independent implementations. It names the shared patterns (the six-method `RendererBase` contract, the `(renderer, events, animator)` triad, per-visual file fan-out, isinstance dispatch) and walks what is unique to each backend. Read this when you are about to write a fourth backend or debug an existing one.

### [philosophy_examples.pdf](./philosophy_examples.pdf)
A pattern catalog for the 50+ scripts under [examples/](../../examples/), showing that every example follows the same skeleton: backend selection, data construction, viewport/camera/model-matrix setup, then a single terminal `renderer.render(...)` call. It explains the five design principles encoded in that skeleton (backend independence, data first / render last, parallel-list rendering API, typed GPU buffers, explicit camera and model-matrix management). Read this when learning the library by example or writing a new example to demonstrate a feature.
