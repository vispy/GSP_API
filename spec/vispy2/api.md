# VisPy2 API - Draft

VisPy2 is the high-level Python producer API for GSP.

Initial public slice should wait until the first GSP point/image/query proof exists.

Desired first API:

```python
import vispy2 as vp

fig, ax = vp.subplots()
ax.imshow(image)
ax.scatter(x, y, color=z, size=3)
fig.show(renderer="datoviz")
fig.savefig("out.svg", renderer="matplotlib")
```

VisPy2 should target GSP, not Datoviz directly.
