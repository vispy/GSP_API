# Install from source

GSP currently requires Python 3.13 or newer and is not published on PyPI.

From a local checkout of `GSP_API`:

```bash
cd GSP_API
uv sync
```

Verify the portable Matplotlib path:

```bash
uv run python examples/review/01_scatter_basic.py --backend matplotlib --offscreen
```

The command writes a PNG and structured run summary under `artifacts/example_review/`. Datoviz is
optional and requires a compatible local v0.4 build; its availability does not imply support for
every GSP capability.
