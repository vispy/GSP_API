# API review examples

The numbered scripts in `examples/review/` are the current compact review surface for GSP and
VisPy2. They cover 2D visuals, guides, color mapping, text, View3D, navigation, lighting, and mesh
picking.

Run one example with the Matplotlib reference backend:

```bash
uv run python examples/review/01_scatter_basic.py --backend matplotlib
```

Compare supported Matplotlib and Datoviz v0.4 paths offscreen:

```bash
tools/compare-review-examples examples/review/01_scatter_basic.py --offscreen
```

Open supported live backends side by side:

```bash
tools/compare-review-examples --live-side-by-side examples/review/07_view3d_cube.py
```

Datoviz results remain capability-gated. An unsupported diagnostic or isolated child-process crash
is evidence, not permission to relabel a capability as strict.

See the [complete review guide](https://github.com/vispy/GSP_API/blob/main/examples/review/README.md)
for the example matrix, interaction controls, artifact layout, and acceptance checklist.
