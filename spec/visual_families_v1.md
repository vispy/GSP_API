# Visual Families v1 - Accepted Baseline

Status: S023 accepted Point/Marker/Segment/Path/Image; S024 TextVisual implementation complete.

S023 establishes the first durable protocol visual-family baseline. The implemented and QA-backed
families are:

| Family | Protocol model | Primary spec | S023 status |
|---|---|---|---|
| Point | `PointVisual` | `spec/visuals/point.md` | accepted |
| Marker | `MarkerVisual` | `spec/visuals/marker.md` | accepted |
| Segment | `SegmentVisual` | `spec/visuals/segment.md` | accepted |
| Path | `PathVisual` | `spec/visuals/path.md` | accepted |
| Image | `ImageVisual` | `spec/visuals/image.md` | accepted |
| Text | `TextVisual` | `spec/visuals/text.md` | accepted and implemented for protocol, Matplotlib reference rendering, QA fixtures, VisPy2 producer API, and item-level Matplotlib query/readback; Datoviz reports structured unsupported diagnostics pending verified v0.4 text semantics |

The v1 baseline is deliberately narrow:

- coordinates are model fields (`coordinate_space`) and are interpreted by backend attachment/view
  mappings;
- colors are final RGBA arrays unless a specific family documents scalar mapping, as ImageVisual
  does for gray/clim scalar images;
- point and marker sizes are rendered screen-pixel diameters;
- segment/path widths are rendered screen-pixel stroke widths;
- v1 visual fields are protocol-owned and backend-native units stay internal.

Deferred visual families and features:

- public `GlyphVisual` and glyph/atlas resources;
- Mesh/Surface/Volume visuals;
- filled polygons, holes, closed path semantics, Beziers, dashes, and arrows;
- colorbars, broad colormap registries, advanced normalization, legends, and layout systems;
- tiled/remote/virtual images as eager ImageVisual fields.

The S023 QA report proving this baseline is generated under
`artifacts/visual_qa/s023/latest-local/` and currently contains 13 cases with both Matplotlib and
Datoviz rendered when the local Datoviz v0.4 binding is active.

## S024 TextVisual addition

S024 adds and implements `TextVisual` as the public text family. `GlyphVisual` is explicitly deferred; glyphs,
atlases, shaping output, and backend text buffers are renderer-internal realization details. Text
font sizes are logical screen pixels, rotation is radians, font selection uses generic `FontRole`,
and printable ASCII plus newline is the required conformance subset.
