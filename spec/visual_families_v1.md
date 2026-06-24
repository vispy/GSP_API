# Visual Families v1 - Accepted S023 Baseline

Status: accepted for S023.

S023 establishes the first durable protocol visual-family baseline. The implemented and QA-backed
families are:

| Family | Protocol model | Primary spec | S023 status |
|---|---|---|---|
| Point | `PointVisual` | `spec/visuals/point.md` | accepted |
| Marker | `MarkerVisual` | `spec/visuals/marker.md` | accepted |
| Segment | `SegmentVisual` | `spec/visuals/segment.md` | accepted |
| Path | `PathVisual` | `spec/visuals/path.md` | accepted |
| Image | `ImageVisual` | `spec/visuals/image.md` | accepted |

The v1 baseline is deliberately narrow:

- coordinates are model fields (`coordinate_space`) and are interpreted by backend attachment/view
  mappings;
- colors are final RGBA arrays unless a specific family documents scalar mapping, as ImageVisual
  does for gray/clim scalar images;
- point and marker sizes are rendered screen-pixel diameters;
- segment/path widths are rendered screen-pixel stroke widths;
- v1 visual fields are protocol-owned and backend-native units stay internal.

Deferred visual families and features:

- Text/Glyph visuals;
- Mesh/Surface/Volume visuals;
- filled polygons, holes, closed path semantics, Beziers, dashes, and arrows;
- colorbars, broad colormap registries, advanced normalization, legends, and layout systems;
- tiled/remote/virtual images as eager ImageVisual fields.

The S023 QA report proving this baseline is generated under
`artifacts/visual_qa/s023/latest-local/` and currently contains 13 cases with both Matplotlib and
Datoviz rendered when the local Datoviz v0.4 binding is active.
