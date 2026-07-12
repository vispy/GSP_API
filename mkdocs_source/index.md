# Graphics Server Protocol

GSP is an experimental, backend-agnostic protocol and Python API for describing scientific 2D and
3D scenes. Matplotlib provides the reference behavior; optional Datoviz v0.4 paths are enabled only
for capabilities supported by the installed facade.

!!! warning "Research prototype"
    GSP and VisPy2 are currently at version `0.1.0`, are not published on PyPI, and may change before
    a stable release.

## Try the current API

GSP requires Python 3.13 or newer and uses `uv` for development environments:

```bash
git clone https://github.com/vispy/GSP_API.git
cd GSP_API
uv sync
uv run python examples/review/01_scatter_basic.py --backend matplotlib
```

The numbered [API review examples](review-examples.md) are the shortest route into the current
surface. They progress from scatter and images through guides, color mapping, View3D navigation,
lighting, and mesh picking.

## Choose the right reference

| Need | Start here |
| --- | --- |
| Understand maturity and backend boundaries | [Status and releases](status.md) |
| Implement or review protocol behavior | [Protocol specification](protocol.md) |
| Use Python packages and types | [API reference](api/gsp.md) |
| Compare renderer behavior | [Testing and conformance](conformance.md) |
| Review small executable scenes | [API review examples](review-examples.md) |
| Understand design history | [Philosophy overview](philosophy/README.md) |

## Architecture at a glance

GSP scene records describe canvases, panels, views, visuals, resources, guides, navigation actions,
and queries without embedding a renderer implementation. VisPy2 is a higher-level producer of GSP
records. Backends consume those records according to explicitly advertised capabilities.

- `gsp`: protocol records, validation, views, queries, resources, and core types
- `vispy2`: experimental plotting-style producer API
- `gsp_matplotlib`: reference renderer
- `gsp_datoviz`: optional legacy renderer and capability-gated Datoviz v0.4 adapter
- `gsp_network`: experimental remote rendering path
- `gsp_pydantic`: serialization support

Backend support is not all-or-nothing. Consult the
[capability matrix](https://github.com/vispy/GSP_API/blob/main/spec/backend_capabilities_visuals.md)
before depending on a renderer-specific behavior.

## Project links

- [Source repository](https://github.com/vispy/GSP_API)
- [White paper](philosophy/whitepaper.md)
- [Changelog](https://github.com/vispy/GSP_API/blob/main/CHANGELOG.md)
- [Issue tracker](https://github.com/vispy/GSP_API/issues)
