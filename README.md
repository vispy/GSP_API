# Graphics Server Protocol (GSP)

GSP is a backend-neutral protocol and Python toolkit for scientific visualization. Version 0.2
defines semantic scenes, validated visual and resource records, explicit capabilities, structured
diagnostics, queries, and a transport-independent session lifecycle.

The repository currently provides:

- `gsp.protocol`: the normative Python protocol surface;
- `gsp_vispy2`: an independent experimental high-level producer (not upstream VisPy 2.0);
- `gsp_matplotlib`: the portable reference renderer;
- `gsp_datoviz`: a capability-gated adapter for a compatible local Datoviz v0.4 build.

GSP is pre-1.0. Version 0.2 deliberately breaks the old `vispy2` import and does not provide a
compatibility alias. Use `gsp_vispy2`.

## Quick start

GSP requires Python 3.13 or newer and is not currently published on PyPI.

```bash
git clone https://github.com/vispy/GSP_API.git
cd GSP_API
uv sync
uv run python examples/docs/first_scene.py --output /tmp/gsp-first-scene.png
```

The executable example uses the current producer API:

```python
import numpy as np
import gsp_vispy2 as vp

fig, ax = vp.subplots()
values = np.array([0.2, 0.8, 0.5, 1.0], dtype=np.float32)
ax.scatter([0, 1, 2, 3], [0.4, 1.2, 0.7, 1.6], c=values, cmap="viridis", clim=(0, 1))
ax.set_xlabel("sample")
ax.set_ylabel("response")
ax.set_title("GSP 0.2 first scene")
fig.savefig("gsp-first-scene.png", dpi=150)
```

`Figure` and `Axes` hold semantic producer state. Rendering is explicit; Matplotlib is the current
public convenience path. A general backend-neutral live display/session API is intentionally not
claimed yet.

## Documentation

- [Public documentation](https://vispy.github.io/GSP_API/)
- [GSP 0.2 consolidated specification](spec/current/index.md)
- [Normative requirement registry](spec/requirements/requirements.json)
- [Implementation profiles and exact support claims](profiles/)
- [Examples](examples/docs/README.md)
- [Contributing](mkdocs_source/contributing.md)

## Validate a checkout

```bash
uv run pytest -q
uv run python tools/spec_traceability.py --check
uv run python tools/profile_consistency.py --check
uv run mkdocs build --strict
```

Datoviz is optional. Its runtime capabilities depend on the active public v0.4 binding and device;
consult runtime discovery and the versioned profile instead of assuming backend parity.

## Legacy code

The older object-oriented `Canvas`/`Viewport`/`RendererBase` system, `GSP_RENDERER`, `datoviz-v03`,
and its examples remain in the repository as historical implementation material. They do not define
GSP 0.2 and are not the recommended user path. See the
[development-history documentation](mkdocs_source/development-history/index.md) for migration rules.

## Project status

GSP 0.2 is an experimental, source-installed development release. No tag, PyPI publication, stable
compatibility guarantee, or general production remote transport is claimed.
