# Visual Cross-Cutting Rules - Accepted S023 Baseline

Status: accepted for S023; extended by S024 TextVisual, S025 MeshVisual, and S026 color mapping
baselines.

These rules apply across S023 visual families unless an individual family spec says otherwise.

## IDs and arrays

- Every visual has a stable protocol `id` validated by `gsp.protocol.validate_id()`.
- Position arrays are finite float32/float64 with shape `(N, 2)` or `(N, 3)`.
- RGBA arrays are uint8 `[0, 255]` or finite float `[0, 1]` with explicit shape documented by the
  family.
- Numeric style arrays are finite and non-negative where they represent rendered size or width.
- Mesh `faces` arrays are integer triangle indices into the visual's `positions` array.

## Units

- Point and marker `sizes` are rendered screen-pixel diameters.
- Segment and path `widths` are rendered screen-pixel stroke widths.
- Text `font_size_px` values are logical screen-pixel font sizes.
- Marker `stroke_width` is a rendered screen-pixel stroke width.
- Matplotlib converts screen pixels to points via figure DPI. Datoviz v0.4 uses `*_px` attributes
  where exposed by the facade.

## Coordinate spaces

- `CoordinateSpace.NDC` and `CoordinateSpace.DATA` are protocol values.
- S023 visual QA fixtures use NDC coordinates over `[-1, +1]`.
- The Datoviz v0.4 adapter maps NDC fixtures to a data-coordinate panel domain configured to
  `[-1, +1]` with equal aspect when available.
- VisPy2 producer examples use `CoordinateSpace.DATA` and render through the Matplotlib reference
  path with semantic `View2D` limits.

## Scope boundaries

S024 defines public `TextVisual` without public glyph resources. S025 defines public `MeshVisual`
without public geometry resources, materials, lights, textures, instancing, surface/volume visuals,
legend, colorbar, tiled-source, remote-source, rich text, layout engines, or interactive editing
semantics.

S026 defines shared color mapping resources and colorbar guides. Scalar color encodings are
slot-specific alternatives to RGBA, not backend mappables or draw-call parameters.

## S027 transform rules

Visual transform bindings are positional only. A visual-local `AFFINE_2D` transform is applied to
source/local positional coordinates before interpreting them in the visual's declared
`CoordinateSpace`.

Transforms affect point centers, marker anchors, segment endpoints, path vertices, text anchors, and
strict 2D mesh vertices. They do not affect screen-pixel sizes, stroke widths, text font size,
scalar color mapping, marker glyph shape, material attributes, or semantic guides. Arbitrary image
rotation/skew is deferred; image placement remains axis-aligned via existing extent plus `View2D`.
