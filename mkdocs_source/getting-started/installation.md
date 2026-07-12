# Install from source

GSP currently requires Python 3.13 or newer and is not published on PyPI.

From a local checkout of `GSP_API`:

```bash
cd GSP_API
uv sync
```

Verify the portable Matplotlib path:

```bash
uv run python examples/docs/first_scene.py --output /tmp/gsp-first-scene.png
```

The command writes a PNG through the current public producer and Matplotlib reference path. Datoviz is
optional and requires a compatible local v0.4 build; its availability does not imply support for
every GSP capability.

The distribution name is `gsp-vispy2`; the import is `gsp_vispy2`. There is deliberately no
`vispy2` compatibility import in 0.2.
