# GSP_API
Graphic Server Protocol Application User Interface

A Python library that provides a unified API for scientific visualization across multiple renderers (Matplotlib, Datoviz).

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

# Datoviz
GSP_RENDERER=datoviz python examples/buffer_example.py
```

---

## Documentation

In-depth design documents live under [docs/philosophy/](docs/philosophy/):

- [Whitepaper](docs/philosophy/whitepaper.md) — backend-agnostic scene-description API for scientific visualization in Python.
- [Philosophy: Packages](docs/philosophy/philosophy_packages.md) — the seven-package split and how dependencies flow downward.
- [Philosophy: GSP Core](docs/philosophy/philosophy_gsp_core.md) — the contract layer (`Canvas`, `Viewport`, `Camera`, `Buffer`, `Visual`).
- [Philosophy: Renderers](docs/philosophy/philosophy_renderers.md) — the `RendererBase` contract and the Matplotlib / Datoviz / Network backends.
- [Philosophy: Examples](docs/philosophy/philosophy_examples.md) — the shared skeleton behind every script in `examples/`.

---

## FAQ

### Q. How do I install it?
A. Create a virtual environment, activate it, and run `pip install -e .` from the project root. See the [Installation](#installation) section above.

### Q. How do I run an example?
A. After installation, run any script under `examples/`, e.g. `python examples/buffer_example.py`. See the [Running](#running) section.

### Q. How do I switch renderers?
A. Set the `GSP_RENDERER` environment variable to either `matplotlib` or `datoviz` before running your script:

```bash
GSP_RENDERER=datoviz python your_script.py
```

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
DVZ_LOG_LEVEL=4 GSP_RENDERER=datoviz python your_script.py
```

### Q. Where is the documentation?
A. Source documentation lives under `mkdocs_source/`. Build it locally with:

```bash
mkdocs serve
```

### Q. Where do I report bugs or request features?
A. Open an issue on the project repository.
