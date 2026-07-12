# First scene

This complete example creates semantic scene records through `gsp_vispy2` and explicitly saves them
through the Matplotlib reference path.

--8<-- "examples/docs/first_scene.py"

Run the exact source shown above:

```bash
uv run python examples/docs/first_scene.py --output /tmp/gsp-first-scene.png
```

The important boundary is deliberate: `Figure` and `Axes` produce semantic GSP records; they do not
contain Matplotlib artists or Datoviz handles. `savefig()` is a current Matplotlib convenience, not a
promise that every renderer implements an interchangeable save method.

The scene contains a `Panel`, `View2D`, `PointVisual`, `PathVisual`, semantic guides, a shared
`ColorScale`, and attachments connecting visuals to their view. Inspect them without rendering:

```python
fig = build_scene()
print(fig.panels())
print(fig.views())
print(fig.visuals())
print(fig.attachments())
```

Next read [Architecture and roles](../concepts/architecture.md), then use the
[producer API](../api/producer.md) and [exact backend matrix](../support/feature-matrix.md).
