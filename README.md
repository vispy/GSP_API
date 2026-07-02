# GSP_API
Graphics Server Protocol Application User Interface

A Python library for backend-agnostic scientific visualization scenes and protocol records, with a
Matplotlib reference backend plus optional Datoviz and network renderer paths.

The current protocol prototype includes 2D visual families, color mapping, guide/layout metadata,
retained `View2D` navigation, static perspective/orthographic `View3D`, bounded 3D mesh rendering, flat Lambert
mesh shading, and first-class query/readback payloads. Matplotlib is the reference backend. Datoviz
v0.4 support is capability-gated against the local v0.4 facade and must not be treated as a required
package dependency.

---

## Installation

Create a virtual environment and install the package in editable mode:

```bash
# Create a virtual environment
python -m venv .venv
source .venv/bin/activate

# Install required packages
pip install -e .
```

Python `>=3.13` is required (see `pyproject.toml`).

---

## Running

Run any of the bundled examples:

```bash
python examples/buffer_example.py
```

Select a renderer with the `GSP_RENDERER` environment variable:

```bash
# Matplotlib (default)
GSP_RENDERER=matplotlib python examples/buffer_example.py

# Legacy Datoviz v0.3 renderer examples
GSP_RENDERER=datoviz-v03 python examples/buffer_example.py
```

---

## Documentation

In-depth design documents live under [docs/philosophy/](docs/philosophy/):

- [Whitepaper](docs/philosophy/markdowns/whitepaper.md) — backend-agnostic scene-description API for scientific visualization in Python.
- [Philosophy: Packages](docs/philosophy/markdowns/philosophy_packages.md) — the seven-package split and how dependencies flow downward.
- [Philosophy: GSP Core](docs/philosophy/markdowns/philosophy_gsp_core.md) — the contract layer (`Canvas`, `Viewport`, `Camera`, `Buffer`, `Visual`).
- [Philosophy: Renderers](docs/philosophy/markdowns/philosophy_renderers.md) — the `RendererBase` contract and the Matplotlib / Datoviz / Network backends.
- [Philosophy: Examples](docs/philosophy/markdowns/philosophy_examples.md) — the shared skeleton behind every script in `examples/`.

---

## FAQ

### Q. How do I install it?
A. Create a virtual environment, activate it, and run `pip install -e .` from the project root. See the [Installation](#installation) section above.

### Q. How do I run an example?
A. After installation, run any script under `examples/`, e.g. `python examples/buffer_example.py`. See the [Running](#running) section.

### Q. How do I switch renderers?
A. Set the `GSP_RENDERER` environment variable to `matplotlib`, `datoviz-v03`, or `network` before running legacy examples that use `examples/common/example_helper.py`:

```bash
GSP_RENDERER=datoviz-v03 python your_script.py
```

Plain `datoviz` is reserved for the Datoviz v0.4 protocol backend. Datoviz legacy renderer support is optional. Install it with `pip install -e ".[datoviz-legacy]"` when using examples that require the older Datoviz Python wrapper.

For protocol/API review, including View2D navigation and View3D mesh examples, see
[`examples/review/README.md`](examples/review/README.md). The Datoviz v0.4 path reports structured
unsupported diagnostics when a local binding lacks the required capability; it does not silently
claim support for unproven features such as View3D mesh triangle picking.

### Q. How do I run the tests?
A. Tests live under `tests/` and run with pytest:

```bash
pytest tests/ -v
```

Or run the full pipeline (lint + tests + examples + expected-output check) via the Makefile:

```bash
make test
```

### Q. How do I use the Makefile?
A. The Makefile is a task runner. List all targets with:

```bash
make help
```

Common targets:

| Target | What it does |
|---|---|
| `make test` | Full pipeline: lint, pytest, run all examples, check expected output |
| `make pytest` / `make pytest_verbose` | Run pytest only |
| `make lint` | Run pyright + ruff |
| `make run_all_examples` | Execute every example script |
| `make clean_output` | Remove generated png/json/pdf/svg/mp4 from `examples/output/` |
| `make stubs_gsp` | Regenerate type stubs |
| `make network_server` | Start the network renderer server |
| `make network_server_dev` | Start the server with auto-restart on file changes |
| `make mkdocs_serve` | Preview docs locally |
| `make mkdocs_build` / `make mkdocs_deploy` | Build / deploy docs to GitHub Pages |

### Q. How do I remove datoviz logs?
A. Set the datoviz log level via the `DVZ_LOG_LEVEL` environment variable. See the [datoviz docs](https://datoviz.org/discussions/CONTRIBUTING/#console-logging).

```bash
DVZ_LOG_LEVEL=4 GSP_RENDERER=datoviz-v03 python your_script.py
```

### Q. Where is the documentation?
A. Source documentation lives under `mkdocs_source/`. Build it locally with:

```bash
mkdocs serve
```

### Q. Where do I report bugs or request features?
A. Open an issue on the project repository.
