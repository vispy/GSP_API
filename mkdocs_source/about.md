# About

## What is GSP?

GSP (Graphic Server Protocol) is a backend-agnostic Python library for describing and rendering 2D and 3D scientific visualizations. It defines a single declarative scene model — canvas, viewports, cameras, visuals, transforms, geometry, materials — and dispatches that scene to one of several interchangeable rendering backends at runtime. The same visualization code runs against a CPU-bound Matplotlib renderer, a GPU-accelerated Datoviz/Vulkan renderer, or a Flask-based network renderer without modification. Backend selection is a one-line change; the scene description is invariant.

## Motivation

Scientific visualization in Python has historically coupled the scene API to the renderer. Matplotlib, Datoviz, VisPy, Plotly, and Bokeh each ship their own scene model and their own rendering pipeline as an indivisible unit. Switching backends means rewriting visualization code. Remote and headless rendering adds a third axis of fragmentation: it is typically implemented as a separate stack with its own protocol, disconnected from local rendering. GSP treats the scene as the invariant and the renderer as the variable. The full problem statement and design rationale are in the [Whitepaper](philosophy/whitepaper.md).

## Key Features

- Unified declarative scene model across all backends (Canvas, Viewport, Camera, eight visual primitives, TransformChain)
- Three first-party renderer backends: Matplotlib, Datoviz, and a network renderer
- Runtime backend selection — `RendererRegistry.create_renderer("matplotlib"|"datoviz"|"network", canvas)` — no code changes required to switch
- Pydantic v2 serialization layer (`gsp_pydantic`) for JSON export and base64-encoded buffer transport
- Network rendering over Flask: client serializes the scene, server renders and returns a PNG
- Python 3.13+ with strict mypy compliance throughout

## Backends

| Backend | Type | Package | Use case |
|---|---|---|---|
| Matplotlib | CPU rasterization | `gsp_matplotlib` | Publication figures, portable environments |
| Datoviz | GPU (Vulkan) | `gsp_datoviz` | Large datasets, interactive high-performance rendering |
| Network | Remote / Flask | `gsp_network` | Headless servers, HPC clusters, cloud notebooks |

## Project Status

GSP is a research prototype at version 0.1.0. It has known bugs, an active TODO list, and no published PyPI release. The architecture is stable enough to run all examples in the [Gallery](gallery.md) against both local backends, but the API may change before a stable release. It is not recommended for production use at this stage.

## Author & Organization

GSP is developed under the [vispy](https://github.com/vispy) GitHub organization. The source repository is at [github.com/vispy/GSP_API](https://github.com/vispy/GSP_API).

## License

BSD 3-Clause License — copyright 2025, vispy. See `LICENSE` in the repository root.

## Contributing

Bug reports, feature requests, and pull requests are welcome on the [GitHub repository](https://github.com/vispy/GSP_API). Please open an issue before submitting a large PR to align on scope and design.
