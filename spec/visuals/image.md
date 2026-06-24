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
- `image` as `(H, W)`, `(H, W, 3)`, or `(H, W, 4)` with uint8 data, finite float scalar data, or float RGB/RGBA data in `[0, 1]`;
- `extent` as `(left, right, bottom, top)`;
- `coordinate_space`, initially `ndc` or `data`;
- `interpolation`, initially `nearest` or `linear`;
- explicit `origin`, initially `upper` or `lower`;
- `colormap`, currently only `gray`, for scalar `(H, W)` images;
- `clim` as optional `(vmin, vmax)` for scalar images.

M003 does not resolve all image coordinate conventions. It makes row origin explicit in the model so Matplotlib does not define the protocol by default.

## M070 v1 hardening

`ImageVisual` v1 remains an eager in-memory visual. Remote, tiled, virtual, chunked, volume, and
colorbar semantics are out of scope.

Validation rules:

- image shape is `(H, W)`, `(H, W, 3)`, or `(H, W, 4)` with positive dimensions;
- uint8 images use native integer channel/scalar values;
- float scalar images may use any finite values and are normalized by `clim` or by their finite
  min/max at render time;
- float RGB/RGBA images must be finite and in `[0, 1]`;
- `extent` must contain four finite values with non-zero width and height;
- `colormap` and `clim` apply only to scalar images;
- S023 supports only the conservative `gray` scalar colormap. Broader colormap registries,
  normalization modes, and colorbars are deferred.

Matplotlib maps scalar images with `cmap="gray"` by default unless `colormap` is explicitly set, and
passes `clim` through with `AxesImage.set_clim()`.

Datoviz v0.4 maps RGB/RGBA images and scalar grayscale images to RGBA8 sampled fields when the
sampled-field binding is present, otherwise to the texture fallback. Origin is represented by
texture coordinates; interpolation is capability-gated by `dvz_image_set_sampling`.

## M011 tiled-source proof

M011 keeps eager `ImageVisual.image` unchanged and adds a separate tiled-source reference proof.
The data source describes availability and materialization; image placement and origin semantics
remain visual/protocol concerns.

The Matplotlib tiled-source helper materializes a viewport mosaic and renders it through the
existing eager image reference path. Future work may add an explicit `data_source_ref` to image
visuals, but M011 does not broaden `ImageVisual`.
