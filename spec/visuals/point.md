# Point Visual - Draft

Semantic purpose: screen-space or world/data-positioned point markers.

First-slice attributes:

| Attribute | Type | Required | Notes |
|---|---|---:|---|
| position | float32/float64 Nx2 or Nx3 | yes | coordinate interpretation from attachment/panel |
| color | rgba8 or transformed scalar/category | yes | final color or color transform source |
| size | float32 N or scalar | yes | screen pixels initially |

Query payload first slice:

- visual id;
- item id;
- data/visual coordinate if available;
- displayed RGBA.
