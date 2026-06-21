# Image Visual - Draft

Semantic purpose: display 2D sampled fields or textures in a panel.

First-slice concepts:

- sampled field or texture source;
- placement rectangle;
- coordinate interpretation;
- interpolation;
- color role;
- optional scalar-to-color mapping.

Open questions:

- row-major upload convention;
- data-coordinate origin;
- texture-coordinate origin;
- vector export fallback.

Query payload first slice:

- visual id;
- texel id or coordinate;
- data coordinate;
- displayed RGBA;
- source value if available.

## M003 first protocol model

`gsp.protocol.ImageVisual` is the first formal image model.

It requires:

- `id`;
- `image` as `(H, W)`, `(H, W, 3)`, or `(H, W, 4)` with uint8 data or float data in `[0, 1]`;
- `extent` as `(left, right, bottom, top)`;
- `coordinate_space`, initially `ndc` or `data`;
- `interpolation`, initially `nearest` or `linear`;
- explicit `origin`, initially `upper` or `lower`.

M003 does not resolve all image coordinate conventions. It makes row origin explicit in the model so Matplotlib does not define the protocol by default.

## M011 tiled-source proof

M011 keeps eager `ImageVisual.image` unchanged and adds a separate tiled-source reference proof.
The data source describes availability and materialization; image placement and origin semantics
remain visual/protocol concerns.

The Matplotlib tiled-source helper materializes a viewport mosaic and renders it through the
existing eager image reference path. Future work may add an explicit `data_source_ref` to image
visuals, but M011 does not broaden `ImageVisual`.
